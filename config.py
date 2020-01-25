from presets import *
#from music import reset_all_listeners
from PyQt5.QtWidgets import *
from fitness import scramble_all
#from PyQt5.QtCore import Qt
import glob
import os
import sys

PRESETS_PATH = 'data/presets/'
MASTER_CONFIG_PATH = 'data/master_'

class Gui(QDialog):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setWindowTitle("Evo Art Puppetmaster")

        self.master_config_dict = load_config(MASTER_CONFIG_PATH)
        self.preset_name = self.master_config_dict['preset_path'].split("/")[-2]
        print(f"loading {self.preset_name} preset")

        self.mainLayout = QGridLayout()

        self.remake_preset_chooser()

        self.remake_dict_editor()
        self.remake_preset_generator()


        self.resize(360, 20)


        #self.scrambleBtn = QPushButton("Scramble all")
        #self.scrambleBtn.clicked.connect(lambda: self.save_master_dict(self.master_config_dict, master_config_path))

    def remake_preset_generator(self):

        try:
            self.PresetGenerator.deleteLater()
        except:
            print()

        self.PresetGenerator = QHBoxLayout()

        self.new_preset_save_btn = QPushButton("Save config as:")
        self.new_preset_save_btn.setEnabled(False)

        self.new_preset_name_editor = QLineEdit('')

        self.new_preset_save_btn.clicked.connect(lambda: self.make_new_preset())
        self.new_preset_name_editor.textChanged.connect(lambda: self.check_new_config_name())

        self.PresetGenerator.addWidget(self.new_preset_save_btn)
        self.PresetGenerator.addWidget(self.new_preset_name_editor)

        self.mainLayout.addLayout(self.PresetGenerator, 4, 0)
        self.setLayout(self.mainLayout)


    def make_new_preset(self):

        name = self.new_preset_name_editor.text()
        create_preset_from_puppetmaster(self.config_dict, name)
        self.new_preset_name_editor.setText('')
        self.new_preset_save_btn.setEnabled(False)
        self.remake_preset_chooser()


    def check_new_config_name(self):

        name = self.new_preset_name_editor.text()
        if name in self.preset_names + ['']:
            self.new_preset_save_btn.setEnabled(False)
        elif self.check_dict():
            self.new_preset_save_btn.setEnabled(True)




    def remake_dict_editor(self):

        try:
            self.DictEditor.deleteLater()
        except:
            print()

        self.create_dict_editor(self.master_config_dict['preset_path'])
        self.mainLayout.addLayout(self.DictEditor, 3, 0)


        # Initialize tab screen
        #self.tabLayout = QGridLayout()
        #self.tabs = QTabWidget()
        #self.tab1 = QWidget()
        #self.tab2 = QWidget()
        #self.tabs.resize(300, 200)
        # Add tabs
        #self.tabs.addTab(self.tab1, "Preset")
        #self.tabs.addTab(self.tab2, "Genes")
        # Create first tab
        #self.tab1.layout = QVBoxLayout(self)
        # self.create_dict_editor(self.master_config_dict['preset_path'])
        #self.tab1.layout.addWidget(self.DictEditor)
        #self.pushButton1 = QPushButton("PyQt5 button 1")
        #self.tab1.layout.addWidget(self.pushButton1)

        #self.mainLayout.addWidget(self.tabs, 3, 0)

        #self.initTabs()
        #self.mainLayout.addLayout(self.tabLayout, 2, 0)

        self.setLayout(self.mainLayout)


    def remake_preset_chooser(self, master_config_path=MASTER_CONFIG_PATH):
        presets = glob.glob(PRESETS_PATH + '*')
        self.preset_names = [x.split(os.sep)[-1] for x in presets]

        try:
            self.PresetChooser.deleteLater()
        except:
            print()

        self.PresetChooser = QHBoxLayout()
        self.presetComboBox = QComboBox()
        self.presetComboBox.addItems(self.preset_names)
        index = self.presetComboBox.findText(self.preset_name)

        if index >= 0:
            self.presetComboBox.setCurrentIndex(index)

        self.presetComboBox.activated.connect(lambda: self.update_master_config())

        presetLabel = QLabel("&Active preset:")
        presetLabel.setBuddy(self.presetComboBox)

        self.selectBtn = QPushButton("Select")
        self.selectBtn.clicked.connect(lambda: self.save_master_dict(self.master_config_dict, master_config_path))

        self.PresetChooser.addWidget(presetLabel)
        self.PresetChooser.addWidget(self.presetComboBox)
        self.PresetChooser.addWidget(self.selectBtn)

        self.mainLayout.addLayout(self.PresetChooser, 1, 0)
        self.setLayout(self.mainLayout)

        
    


    def update_master_config(self):

        self.master_config_dict = load_config(MASTER_CONFIG_PATH)
        self.preset_name = str(self.presetComboBox.currentText())
        self.master_config_dict['preset_path'] = PRESETS_PATH + self.preset_name + '/'
        self.remake_dict_editor()


    def create_dict_editor(self, preset_path):

        self.widgets = {}
        self.DictEditor = QFormLayout()
        self.config_dict = load_config(preset_path)
        for key, value in self.config_dict.items():
            self.widgets[key] = widget = {}
            widget['lineedit'] = lineedit = QLineEdit(str(value))
            widget['lineedit'].textChanged.connect(lambda: self.check_dict())
            self.DictEditor.addRow(key, lineedit)

        self.saveBtn = QPushButton("Save config")
        self.saveBtn.clicked.connect(lambda: self.save_config_dict(self.config_dict, preset_path))
        self.DictEditor.addRow(self.saveBtn)
        self.check_dict()


    def check_dict(self):

        try:
            n_parameters = len(self.config_dict["natures"])
            for key, value in self.config_dict.items():
                value = eval(self.widgets[key]['lineedit'].text())
                print(value)
                if type(value) == list and key not in ["natures", "synths", "manual_optimum"]:
                    print(key)
                    if len(value) != n_parameters:
                        print("Here I die")
                self.config_dict[key] = value
            self.saveBtn.setEnabled(True)
            return True
        except:
            self.saveBtn.setEnabled(False)
            try:
                self.new_preset_save_btn.setEnabled(False)
            except:
                print()
            return False


    def save_config_dict(self, config_dict, config_path):

        for key, value in config_dict.items():
            config_dict[key] = eval(self.widgets[key]['lineedit'].text())
            if key == "natures":
                config_dict[key] = sorted(config_dict[key])

        done = False
        while not done:
            try:
                save_config(config_path, config_dict)
                print(f"saving config file as {config_path}config.json")
                done = True
            except:
                print(f"save of {config_path}config.json failed")

        preset_path = self.master_config_dict["preset_path"]

        for nature in config_dict["natures"]:
            if not os.path.isfile(preset_path + f"current/{nature.lower()}.csv"):
                create_initial_genes(preset_path + f"current/", config_dict, nature)

        files = [file.replace('\\', '/') for file in glob.glob(preset_path + 'current/*.csv') if 'playing' not in file]
        print(config_dict["natures"])
        for file in files:
            if file.split(os.sep)[-1].split('.')[0].upper() not in config_dict["natures"]:
                print(file.split('/')[-1].split('.')[0].upper())
                #os.remove(file.replace('\\', '/'))


    def save_master_dict(self, config_dict, config_path):

        done = False
        while not done:
            try:
                save_config(config_path, config_dict)
                print(f"saving config file as {config_path}config.json")
                done = True
            except:
                print("save master config failed")
        self.update_master_config()


    """
    
    def create_top_layout(self):

        self.topLayout = QHBoxLayout()
        self.styleLabel = QLabel("Here you can edit the preset config file.")
        self.topLayout.addWidget(self.styleLabel)
        
        
    def initTabs(self):

        # Initialize tab screen
        self.tabLayout = QGridLayout()
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300, 200)
        # Add tabs
        self.tabs.addTab(self.tab1, "Preset")
        self.tabs.addTab(self.tab2, "Genes")
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        #self.create_dict_editor(self.master_config_dict['preset_path'])
        #self.tab1.layout.addWidget(self.DictEditor)
        #self.pushButton1 = QPushButton("PyQt5 button 1")
        #self.tab1.layout.addWidget(self.pushButton1)
        # Create second tab
        self.tab2.layout = QVBoxLayout(self)
        #self.pushButton2 = QPushButton("PyQt5 button 2")
        #self.tab2.layout.addWidget(self.pushButton2)
        self.tabLayout.addWidget(self.tabs)
    """

#app = QApplication(sys.argv)
#gui = Gui()
#gui.show()
#sys.exit(app.exec_())

def get_available_samples():

    master_config_dict = load_config(MASTER_CONFIG_PATH)

    available_samples = {}
    #natures = [x for x in glob.glob(f"samples{os.sep}*")]
    natures = [x for x in glob.glob(os.path.join('samples', '*'))]
    natures.sort()

    # add synths

    for nature in natures:
        #samples = [x for x in glob.glob(f"{nature}{os.sep}*")]
        folder = os.path.join(nature, '*')
        samples = []
        for x in glob.glob(folder):
            filename = str(os.path.normpath(x))
            samples.append(filename)

        available_samples[nature.split(os.sep)[-1]] = samples

    
    master_config_dict["available_samples"] = available_samples
    master_config_dict["n_available_samples"] = [len(x) for x in available_samples.values()]

    save_config(MASTER_CONFIG_PATH, master_config_dict)

    return master_config_dict


def check_for_playing(preset_path):

    if not os.path.isfile(preset_path + "playing.csv"):
        select_genes(preset_path)


def main():

    master_config_dict = get_available_samples()
    check_for_playing(master_config_dict["preset_path"])
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    gui = Gui()
    gui.show()
    sys.exit(app.exec_())