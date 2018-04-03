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

# [START startup]
set -v
PROJECTID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
# [START logging]
curl -s "https://storage.googleapis.com/signals-agents/logging/google-fluentd-install.sh" | bash
service google-fluentd restart &
# [END logging]


apt-get update
apt-get install -yq git build-essential supervisor python3 python3-dev python-pip libffi-dev libssl-dev


# Create a pythonapp user. The application will run as this user.
useradd -m -d /home/pythonapp pythonapp
##................................ pip from apt is out of date, so make it update itself and
pip install --upgrade pip virtualenv

export HOME=/root
rm -r /opt/app
git config --global credential.helper gcloud.sh
#................................
git clone https://source.developers.google.com/p/$PROJECTID/r/HelloWorld /opt/app

virtualenv -p python3 /opt/env
/opt/env/pip install -r /opt/app/CheckScoreTin/requirements.txt


##................................ Make sure the pythonapp user owns the application code
chown -R pythonapp:pythonapp /opt/app
cat >/etc/supervisor/conf.d/python-app.conf << EOF
[program:pythonapp]
directory=/opt/app/CheckScoreTin
command=/opt/env/bin/gunicorn main:server --bind 0.0.0.0:8080
autostart=true
autorestart=true
user=pythonapp
# Environment variables ensure that the application runs inside of the
# configured virtualenv.
environment=VIRTUAL_ENV="/opt/env/CheckScoreTin",PATH="/opt/env/bin",\
    HOME="/home/pythonapp",USER="pythonapp"
stdout_logfile=syslog
stderr_logfile=syslog
EOF
supervisorctl reread
supervisorctl update
# [END startup]
