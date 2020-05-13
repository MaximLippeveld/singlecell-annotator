from django.apps import AppConfig
import javabridge
import bioformats


class SinglecellConfig(AppConfig):
    name = 'singlecell'

    def ready(self):
        # javabridge.start_vm(class_path=bioformats.JARS)
        pass
