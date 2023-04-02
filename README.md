# DIP (Datasets for Improving Photogrammetry)
Photogrammetry acquisition simulation software

 [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center"><b>Dataset for Improving Photogrammetry</b></h3>

  <p align="center">
    Symulation software for rendering photogrammetric setups
    <br />
    <a href="https://github.com/HoenikkerPerez/DIP"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/HoenikkerPerez/DIP/issues">Report Bug</a>
    ·
    <a href="https://github.com/HoenikkerPerez/DIP/issues">Request Feature</a>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
       <a>Getting Started</a>
      <ul>
        <li><a href="#getting-started-with-windows">Windows</a></li>
        <li><a href="#getting-started-with-linux-or-macos">Linux</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
# About
Python is a software that allows you to render images, simulating a photogrammetric acquisition. Acquisition parameters such as lighting setup, models, materials, scene composition can be customized.



<!-- GETTING STARTED -->
# Getting Started

## Requisites
1. Download and install Blender from: https://www.blender.org/download
2. Clone the repository:
   ```sh
   git clone https://github.com/FiRMLAB-Pisa/pySynthMRI.git
   ```
3. Create a [Python Virtual Environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
4. Install required libraries:
   ```sh
   pip install -r requirements.txt
   ```


<!-- USAGE EXAMPLES -->
# Usage
The software che be run both using Blender GUI or CLI:
   ```sh
   blender --background --python recon_all.py
```
### Configuration
In order to correctly execute DPI, `config.json` file need to be created.
A default configuration file (`config-sample.json`) is provided for reference. <br/>
We suggest to copy sample file:

```sh
   cp config-sample.json config.json
```
    
Below part of the configuration file is reported for help.


<!-- LICENSE -->
## License

DPI is distributed under MIT License. See [LICENSE.txt](https://github.com/HoenikkerPerez/DIP/blob/main/LICENSE) for more information.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/HoenikkerPerez/DIP
[contributors-url]: https://github.com/HoenikkerPerez/DIP/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/HoenikkerPerez/DIPI
[forks-url]: https://github.com/HoenikkerPerez/DIP/forks
[stars-shield]: https://img.shields.io/github/stars/HoenikkerPerez/DIP 
[stars-url]: https://github.com/HoenikkerPerez/DIP/stargazers
[issues-shield]: https://img.shields.io/github/issues/HoenikkerPerez/DIP
[issues-url]: https://github.com/HoenikkerPerez/DIP/issues
[license-shield]: https://img.shields.io/github/license/HoenikkerPerez/DIP
[license-url]: https://github.com/HoenikkerPerez/DIP/blob/master/LICENSE.md
[pysynthmri-arch]: resources/images/arch.png
[pysynthmri-screenshot]: resources/images/screenshot.png
