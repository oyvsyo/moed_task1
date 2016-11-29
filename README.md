# Task1

Task1 is the open source project for spectrum modulation designed by Dvoiak Stepan,  
Kiev National University student for MOED course.  
This program can modulate peaks, compton and background by parameters.


## Getting Started

Clone this repo to your local machine:

```
$ git clone https://github.com/oyvsyo/moed_task1.git
```
To start nodulation jus run this command in terminal (bash shell or mac shell) in project directory:

```
$ python2 task1.py
```
You will see two windows (left - for config window, rigth - for drawing spectrums).  
In config window you can set parameters of spectrums, load configurations, save configuration,
 save spectrums in txt file and eps pictures.    

## Default parameters

To draw simple default specters just press red button <kbd>Draw</kbd>.  
You got spectrums on canvas (drawing window)  
If you want to clear all entries - press pink button <kbd>Clear All</kbd>.  
If you want to set defaul parameters again - press <kbd>Default</kbd> button.  

## Your own configuration

The best way to set you own spectrum parameters - it's change defaul!   
All rules and sintaxys diclarated in next paragraf.
  
Also, you can write config file manualy (syntaxis - like json  
or standart python dict)  
To load your file - simply open menu <kbd>File->Open config</kbd>

## The rules of config file
Concept of config file is python dict - structure of  "key": "value"  
pairs.
There are 6 keys of parameters:
* __interval__ - the python list of two values: minimum and maximum  
of Energy range of investigated spectrum `[Emin, Emax]` (*unsigned float*)
* __num_bin__ - number channels (*unsigned interer*)
* __peaks__ - it's a python list of three dimentional lists with peaks   
parameters values `[Intensity(1/s), Energy(keV), FWMH(keV)] `(*unsigned float*)  
* __opt1__ - optional chose for FWHM simulation (integer 1 or 0), if 0 - FWHM gets   
from last peak parameters, if 1 - FWHM is calculated by formula: <kbd>a0+a1*sqrt(E)</kbd>
* __FWHM_pars__ - the parameters of FWHM formula `[a0, a1]` (*float numbers*)
* __background__ - parameters of background simulation formula:   
<kbd>a\*exp(b* E) + c+d* E</kbd> (*float numbers*)

>Notice! Its not recomendet to set `num_bin` parameter over 1000.   
>Calculating can take too much time (4 seconds on my computer).  
>Operations numbers increase like (num_bin)^2 times.

Also you can comment some text with `"<"` and `">"` symbols like:  
`<comment here>`.

>Notice! You can't use `"<"` and `">"` symbols inside comment.

An example of default confuguration file:
```
<spectrum simulation>
<config file example>
<after square brackets "[..]" always put ",">
<all parameters must be set>
{
    <Energy(keV) range - must be positive:>
    'interval': [50, 3000],
    <number of bins (put "," after bin number value):>
    <must be positive int number>
    'num_bin': 300,

    <peaks parameters sets in square brackets>
    <in defined order: [Intensity(1/s), Energy(keV), FWMH(keV)]>
    <peaks parameters must be positive>
    'peaks':[
        [15000, 2000.89, 150.8],
        [14000, 1400.5, 135.0],
        [13000, 1000, 131.0],
        [17000, 1200, 75.0],
        [12000, 2999, 50.0],
    ],

    <optional chose for FWMH simulation>
    < 0 - FWMH is set from peak parameters>
    < 1 - calculating by formula: FWHM = a0+a1*sqrt(E)>
    <after opt1 value put ",">
    "opt1": 1,

    <set the FWMH params for formula FWHM = a0+a1*sqrt(E)>
    <if opt1=1 [a0, a1]:>
    "FWHM_pars": [0.5, 1],

    <background parameters [a, b, c, d] : a*exp(b*E) + c+d*E>
    <parameter 'a' must be positive>
    'background': [40, -0.01, 50, -0.005],
}

```

>Notice! The config file must have `.txt` exestention

## Using GUI
The main logic based on config file syntax.  
The simplest way - just edit default parameters!  

To set parameters with GUI you need to know some rules:  
1. All entries are required.  
2. Enter the vaule of "key":"value" pairs from config file.   
3. If key value is list - write parameters in list format (like [a, b, c]).    
4. For FWMH simulation by formula: FWHM = a0+a1*sqrt(E) just check   
<kbd>FWHM optin calculate</kbd> checkbuttun   
5. Other parameters sets like vaule vor keys in config file dict.

>Notice! GUI does not support comments.

Example for peak entry:  
```
[[14000, 2700.89, 110.8]
 [16000, 700.5, 135.0]
 [17000, 1600, 75.0]]
```
>Ntice: for peaks its not nessecery to write `","` after `"]"`
  
To save your comfiguration press <kbd>File->Save config as..</kbd>  
and enter name.

## Saving results of simulation
To save a pictures and .txt files of simulated spectrum press   
<kbd>File->Save output to..</kbd>  and write a path to directory that   
will be created for yuor output files (dir name - *name_out*).  
You can find 4 eps pictures and 4 txt spectrum files. (txt files - its
two columns of float numbers - first - energy, second - counts).



### Requirments
This software is require python 2.7* versions, some standart for ubuntu 14.04 python librarys:
- math
- re
- os
- ast
- sys
- Tkinter
- tkFileDialog
- tkMessageBox   

There are one non standart library:
- numpy 1.8.2

And tha main core of simulation - __ROOT__.
>Notice! For using this program you must have ROOT classes avaliable in python scope. Read more about [PyRoot](https://root.cern.ch/pyroot)

>Notice! ROOT 5.* versions are required (probably must works on 6.* versions, but not tested)

>Tested on ubuntu 14.04 whith python 2.7.6 and ROOT 5.34/36, gcc 4.8.4 

## Authors

**Dvoiak Stepan** - [oyvsyo](https://github.com/oyvsyo)

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the [LICENSE](LICENSE) file for details