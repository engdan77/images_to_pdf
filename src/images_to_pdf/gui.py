from pywebio.output import put_progressbar

from . import runmode
from pywebio.input import input_group, input, NUMBER, select, checkbox
from pywebio_battery import file_picker, put_logbox
import userpaths
from . import logger


def main():
    runmode.set_runmode('gui')
    put_logbox("log")

    logger.info(f"Start {__package__} {__version__}")

    params = input_group("Parameters", [
        file_picker(title="Select image folder with images", multiple=False, path='~'),
        file_picker(title="Select output folder for PDF", multiple=False, path='~'),
        input('Images per page: ', type=NUMBER, name='images_per_page', value=10),
        input('Max pages per PDF: ', type=NUMBER, name='max_pages_per_pdf', value=20),
        select(label='Layout', options=['grid', 'auto', 'lane', 'document'], name='layout', value='grid', help_text='Document for single page per image'),
        select(label='Resolution', options=[
            {'label': 'big', 'value': (1754, 1240), 'selected': True},
            {'label': 'medium', 'value': (877, 620)},
            {'label': 'small', 'value': (584, 413)}
        ], name='resolution', help_text='Smaller result in smaller file'),
        checkbox(label='Annotate images', options=['filename'], name='annotate_images', value=[], help_text='Add filename as part of the image'),
    ])

    put_progressbar('outer')
    put_progressbar('inner')

    '''
    def create_pdf(image_path: ExistingDirectory,
               output_pdf: ResolvedFile,
               images_per_page: int = 10,
               max_pages_per_pdf: int = 20,
               layout: Literal['grid', 'auto', 'lane', 'document'] = "grid",
               resolution: tuple[int, int] = (1754, 1240),
               annotate_images: Annotated[bool, Parameter(help='Add filename as part of the image')] = False,

    '''

if __name__ == '__main__':
    main()