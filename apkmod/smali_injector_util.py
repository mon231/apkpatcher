from pathlib import Path


class ActivitySmaliInjector:
    def __init__(self, sources_path: Path, activity_name: str):
        self.__activity_file = ActivitySmaliInjector.__find_activity_source_file(sources_path, activity_name)
        activity_content = self.__activity_file.read_text()

        self.__direct_methods_end = activity_content.find('# virtual methods')
        self.__direct_methods_start = activity_content.find('# direct methods')

        if (self.__direct_methods_start == -1) or (self.__direct_methods_end == -1):
            raise Exception('Couldn\'t find direct & virtual methods sections')

    def inject_to_activity(self, code_to_inject: str):
        activity_content = self.__activity_file.read_text()

        class_constructor_start_index = activity_content.find(
            '.method static constructor <clinit>()V',
            self.__direct_methods_start,
            self.__direct_methods_end
        )

        if class_constructor_start_index == -1:
            self.__patch_activity_without_class_constructor(code_to_inject)
        else:
            self.__patch_activity_with_class_constructor(code_to_inject)

    def __patch_activity_without_class_constructor(self, injected_code: str):
        main_activity_loader = \
'''
.method static constructor <clinit>()V
    .locals 1
    .prologue
    {0}
    return-void
.end method
'''.format(injected_code)

        activity_content = self.__activity_file.read_text()
        loader_begin_index = self.__direct_methods_start + len('# direct methods') + 1

        new_content = activity_content[0:loader_begin_index]
        new_content += main_activity_loader
        new_content += activity_content[loader_begin_index:]

        self.__activity_file.write_text(new_content)

    def __patch_activity_with_class_constructor(self, injected_code: str):
        activity_content = self.__activity_file.read_text()

        class_constructor_start_index = activity_content.find(
            '.method static constructor <clinit>()V',
            self.__direct_methods_start,
            self.__direct_methods_end
        )

        class_constructor_end_index = activity_content.find(
            '.end method',
            class_constructor_start_index,
            self.__direct_methods_end
        )

        if class_constructor_end_index == -1:
            raise Exception('Error unexpected class constructor end')

        class_constructor_prologue_index = activity_content.find(
            '.prologue',
            class_constructor_start_index,
            class_constructor_end_index
        )

        if class_constructor_prologue_index != -1:
            self.__patch_constructor_with_prologue(injected_code, class_constructor_start_index, class_constructor_end_index)
        else:
            self.__patch_constructor_with_locals(injected_code, class_constructor_start_index, class_constructor_end_index)

    def __patch_constructor_with_prologue(self, injected_code: str, class_constructor_start_index: int, class_constructor_end_index: int):
        activity_content = self.__activity_file.read_text()

        prologue_start_index = activity_content.find(
            '.prologue',
            class_constructor_start_index,
            class_constructor_end_index
        )

        if prologue_start_index == -1:
            raise Exception('Error couldn\'t find class-constructor prologue')

        prologue_end_index = activity_content.find('\n', prologue_start_index, class_constructor_end_index) - 1

        if prologue_end_index == -1:
            raise Exception('Error couldn\'t parse class-constructor post prologue')

        new_content = activity_content[:prologue_end_index + 1]
        new_content += f'\n{injected_code}\n'
        new_content += activity_content[prologue_end_index + 1:]

        self.__activity_file.write_text(new_content)

    def __patch_constructor_with_locals(self, injected_code: str, class_constructor_start_index: int, class_constructor_end_index: int):
        activity_content = self.__activity_file.read_text()

        locals_start_index = activity_content.find(
            '.locals ',
            class_constructor_start_index,
            class_constructor_end_index
        )

        if locals_start_index == -1:
            raise Exception('Error couldn\'t find class-constructor locals')

        locals_end_index = activity_content.find('\n', locals_start_index, class_constructor_end_index) - 1

        if locals_end_index == -1:
            raise Exception('Error couldn\'t parse class-constructor post locals')

        new_content = activity_content[:locals_end_index]

        if activity_content[locals_end_index] == '0':
            new_content += '1'
        else:
            new_content += activity_content[locals_end_index]

        new_content += '\n\t.prologue\n'
        new_content += injected_code + '\n'
        new_content += activity_content[locals_end_index+1:]

        self.__activity_file.write_text(new_content)

    @staticmethod
    def __find_activity_source_file(sources_path: Path, activity_name: str) -> Path:
        for smali_folder in sources_path.glob('**/smali*'):
            activity_path = smali_folder / (activity_name.replace('.', '/') + '.smali')

            if activity_path.is_file():
                return activity_path

        raise Exception(f'Activity smali file was not found')
