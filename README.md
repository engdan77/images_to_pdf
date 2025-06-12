# 🌄 Images to PDF 📄



## Background

Many times in my past I've missed a tool for easily converting number of images into one or many PDF files á la "collage" (various sizes), "grid" (side-by-side), and adjust the quality and therefore the size on-the-fly as well as when my wife been asking how she'd convert "photographed" A4 pages into PDF so I took a swing and developed this little tool that for sure will aid me and perhaps other may find use of.



## Features

- Scans folder recursivelt and converts from common image formats such as PNG, JPG, TIFF to multi-page PDF's
- Different layouts such as 
  - Auto (collage)
  - Grid (side-by-side rows and columns)
  - Lane (broad images in row)
  - Document (suitable for scanned A4 one per page)
- Limit number of images per page
- Limit number of pages per PDF (splits as found needed)
- Optionally include filenames (properly formatted, e.g. support for new lines) inlined within images
- Shuffle the order of images



## How to run - with no need to install

Ensure you have UV the package installed following [this](https://docs.astral.sh/uv/guides/install-python/) instruction, then run the following command

### GUI version

```she
uvx --from https://github.com/engdan77/images_to_pdf.git images-to-pdf-gui <image path optionally>
```

<img src="https://raw.githubusercontent.com/engdan77/project_images/master/pics/image-20250612143434593.png" alt="image-20250612143434593" style="zoom:50%;" />

### CLI version

```
uvx --from https://github.com/engdan77/images_to_pdf.git images-to-pdf
```

![image-20250612143617919](https://raw.githubusercontent.com/engdan77/project_images/master/pics/image-20250612143617919.png)