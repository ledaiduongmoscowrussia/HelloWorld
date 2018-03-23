
#! /bin/bash
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -v
PROJECTID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
# [START logging]
curl -s "https://storage.googleapis.com/signals-agents/logging/google-fluentd-install.sh" | bash
service google-fluentd restart &
# [END logging]

# Install dependencies from apt
apt-get update
alias python=python3
apt-get install -yq \
    git build-essential supervisor python python-dev python-pip libffi-dev \
    libssl-dev

#................................ Create a pythonapp user. The application will run as this user.
useradd -m -d /home/pythonapp pythonapp


#................................ Get the source code from the Google Cloud Repository
export HOME=/root
rm -r /opt/app
git config --global credential.helper gcloud.sh
git clone https://source.developers.google.com/p/$PROJECTID/r/HelloWorld /opt/app

#................................ Install app dependencies
virtualenv -p python3 /opt/app/CheckScoreTin/env
#................................ pip from apt is out of date, so make it update itself and install virtualenv.
pip install --upgrade pip virtualenv
/opt/app/CheckScoreTin/env/bin/pip install -r /opt/app/CheckScoreTin/requirements.txt

#................................ Make sure the pythonapp user owns the application code
chown -R pythonapp:pythonapp /opt/app

#................................ Configure supervisor to start gunicorn inside of our virtualenv and run the
cat >/etc/supervisor/conf.d/python-app.conf << EOF
[program:pythonapp]
directory=/opt/app/CheckScoreTin
command=/opt/app/CheckScoreTin/env/bin/gunicorn main:app --bind 0.0.0.0:8080
autostart=true
autorestart=true
user=pythonapp
# Environment variables ensure that the application runs inside of the
# configured virtualenv.
environment=VIRTUAL_ENV="/opt/app/env/CheckScoreTin",PATH="/opt/app/CheckScoreTin/env/bin",\
    HOME="/home/pythonapp",USER="pythonapp"
stdout_logfile=syslog
stderr_logfile=syslog
EOF

supervisorctl reread
supervisorctl update

#................................ Application should now be running under supervisor
#................................ [END startup]