from sklearn.preprocessing import LabelEncoder


regime = 1

if regime == 3 :
    import sshtunnel
    sshtunnel.SSH_TIMEOUT = 5.0
    sshtunnel.TUNNEL_TIMEOUT = 5.0
    ssh = ('ssh.pythonanywhere.com');
    un = 'ledaiduongvnth';
    pwd = 'leduysao290893';
    lcad = ('localhost', 3333);
    rmad = ('ledaiduongvnth.mysql.pythonanywhere-services.com', 3306)



# English
EnglishCategory = ['Pronunciation', 'Stress',
                   'Noun', 'Adjective_Adverb','Conjunction', 'Articles_a_an_the',  'Prepositions', 'Phrasal_verb', 'Verb',
                   'Verb_tenses','Relative_clause',
                   'Direct_indirect_sentence','Comparison', 'Identify_formation_of_words',
                   'Synonyms', 'Antonyms',
                   'Error_identification', 'Sentence_transformation',
                   'Reading',
                   'Pronoun', 'Model_verb', 'Passive_voice','Conditinal','Gerund_infinitive_participle','Tag_Question','Inversion', 'Subject_verb_agreement']
# Math
MathCategory = ['Survey_of_variation_and_plot_of_functions',
                'Trigonometric_equations',
                'Equation, unequation,system_of_equations',
                'Integral',
                'Geometry_of_space',
                'Inequalities, finding_of_max_min_values',
                'Plane_geometry',
                'Space_analysis_geometry',
                'Combination_Probability, Newtonian_binary',
                'Complex_numbers']
# Physics
PhysicsCategory = ['Mechanical_oscillation',
                   'Mechanical_waves',
                   'Alternating_current',
                   'Oscillation_and_electromagnetic_waves',
                   'Light_waves',
                    'Quantum_of_light',
                   'Atomic_nucleus']
PhysicsIndicatorsDict = {'Mechanical_oscillation': ['ao động điều', 'ao động cơ', 'lò xo'],
                        'Mechanical_waves': ['sóng cơ', 'sóng dừng', 'sợi dây', 'mặt nước'],
                        'Alternating_current': ['điện áp', 'xoay chiều', 'LC', 'RLC', 'mạch dao động', 'mạch điện'],
                        'Oscillation_and_electromagnetic_waves': ['điện tích', 'từ trường', 'sóng vô tuyến'],
                        'Light_waves': ['ánh sáng', 'iao thoa', 'quang phổ', 'thấu kính'],
                         'Quantum_of_light':['giới hạn quang dẫn', 'ăng lượng kích hoạt', 'giải phóng một êlectron', 'tia X'],
                        'Atomic_nucleus': ['hạt nhân', 'nhiệt hạch', 'nguyên tử']}
PhysicsIndicatorsList = list(PhysicsIndicatorsDict.values())
Categories = {'English': EnglishCategory,
            'Math': MathCategory,
            'Physics': PhysicsCategory}
list_pos_tag = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
LabelEncoderPosTag = LabelEncoder()
LabelEncoderPosTag.fit(list_pos_tag)
list(LabelEncoderPosTag.classes_)
LabelEncoderEnglishCategory = LabelEncoder()
LabelEncoderEnglishCategory.fit(EnglishCategory)
list(LabelEncoderEnglishCategory.classes_)
list_delimiters_0 = ['Mark the letter', 'Blacken the letter', 'Read the following', 'THE END', 'ĐÁP ÁN']
list_delimiters_physics = ['Câu', 'HẾT']
Subjects = ['English', 'Math','Physics']
Algorithm = ['K nearest neighbor', 'Support vector machine', 'Tree decision']
Options = ['A', 'B', 'C', 'D']






