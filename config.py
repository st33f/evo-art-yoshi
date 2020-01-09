from presets import *
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

        self.create_preset_chooser()
        self.mainLayout.addLayout(self.PresetChooser, 1, 0)

        self.remake_dict_editor()
        self.resize(540, 20)


        #self.scrambleBtn = QPushButton("Scramble all")
        #self.scrambleBtn.clicked.connect(lambda: self.save_master_dict(self.master_config_dict, master_config_path))


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


    def create_preset_chooser(self, master_config_path=MASTER_CONFIG_PATH):
        presets = glob.glob(PRESETS_PATH + '*')
        preset_names = [x.split(os.sep)[-1] for x in presets]

        self.PresetChooser = QHBoxLayout()
        self.presetComboBox = QComboBox()
        self.presetComboBox.addItems(preset_names)
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
            for key, value in self.config_dict.items():
                self.config_dict[key] = eval(self.widgets[key]['lineedit'].text())
            self.saveBtn.setEnabled(True)
        except:
            self.saveBtn.setEnabled(False)


    def save_config_dict(self, config_dict, config_path):

        for key, value in config_dict.items():
            config_dict[key] = eval(self.widgets[key]['lineedit'].text())

        done = False
        while not done:
            try:
                save_config(config_path, config_dict)
                print(f"saving config file as {config_path}config.json")
                done = True
            except:
                print(f"save of {config_path}config.json failed")


    def save_master_dict(self, config_dict, config_path):

        done = False
        while not done:
            try:
                save_config(config_path, config_dict)
                print(f"saving config file as {config_path}config.json")
                done = True
            except:
                print("save master config failed")


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
    natures = [x for x in glob.glob('samples/*')]
    for nature in natures:
        samples = [x for x in glob.glob(nature+'/*')]
        available_samples[nature.split('/')[-1]] = samples
        print(nature, samples)
    print(available_samples)
    
    master_config_dict["available_samples"] = available_samples
    master_config_dict["n_available_samples"] = [len(x) for x in available_samples.values()]

    save_config(MASTER_CONFIG_PATH, master_config_dict)


def main():

    get_available_samples()
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    gui = Gui()
    gui.show()
    sys.exit(app.exec_())