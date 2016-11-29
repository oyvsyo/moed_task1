"""
This program allowes you to moduling phisical spectrums.
To start just execut a command in terminal: $ python2 task1.py
"""
from __future__ import division
import ROOT
import math
import re
import os
import ast
import sys
import numpy
import Tkinter
import tkFileDialog
import tkMessageBox


# ------setup gui ---------------
about_text = """
Welcome to task1

Task1 is the open source project for spectrum modulation designed by Dvoiak Stepan,  
Kiev National University student for MOED course.  
This program can modulate peaks, compton and background by parameters.

This project is licensed under the GNU GENERAL PUBLIC License, 
see the LICENSE file for details

For help pres menu Help->Help
"""

help_text = """
Help refrenses:

To draw simple default specters just press red button "Draw".  
You got spectrums on canvas (drawing window)  
If you want to clear all entries - press pink button "Clear All".  
If you want to set defaul parameters again - press "Default"" button.  
*   *   *
Rules for config by GUI:
1. All entries are required.
2. Enter the vaule of "key":"value" pairs from config file.
3. If key value is list - write parameters in list format (like [a, b, c]), peaks:

!! Notice: GUI does not support comments.
!! Ntice: for peaks its not nessecery to write `","` after `"]"`

"""

window = Tkinter.Tk()
window.geometry("550x480+0+0")
window.wm_title("Config window")

peak_entry = Tkinter.Text(window, height=10, width=50)
bg_entry = Tkinter.Entry(window)
energy_entry = Tkinter.Entry(window)
bin_entry = Tkinter.Entry(window)

load_var = Tkinter.StringVar()
load_label = Tkinter.Label(window, textvariable=load_var)
load_var.set("To open config file pres menu File->Open config")

opt_FWHM = Tkinter.IntVar()
FWHM_check = Tkinter.Checkbutton(window,
                                 text="FWHM optin calculate",
                                 variable=opt_FWHM)
FWHM_entry = Tkinter.Entry(window)

peak_label = Tkinter.Label(window, text="Enter peaks: \n [intensity 1/sec, energy kev, FWHM kev]")
energy_label = Tkinter.Label(window, text="Enter energy range:\n [Emin, Emax]")
bin_label = Tkinter.Label(window, text="Enter bin numbers:")
FWHM_label = Tkinter.Label(window, text="Enter FWHM parameters:\n [a1, a2]")
bg_label = Tkinter.Label(window, text="Enter background parameters:\n [a, b, c, d]")

histograms = []
c1 = ROOT.TCanvas("first", "Spectrums", 550, 0, 820, 600)
c1.Divide(2, 2)
c1.SetGrid()
ROOT.gStyle.SetOptStat(0)

default_data_dict = {
    'FWHM_pars': [0.5, 2],
    'num_bin': 300,
    'interval': [50, 3000],
    'background': [4, -0.01, 50, -0.005],
    'opt1': 0,
    'peaks': [
        [15000, 2000.89, 150.8],
        [14000, 1400.5, 135.0],
        [13000, 1000, 131.0],
        [17000, 1200, 75.0],
        [12000, 2999, 50.0],
    ],
}


def compton(x, E, I):
    """Return value of Klein-Nishina function."""
    if (x < E*2*E/511/(1+2*E/511)):
        return I/E*(2 - 2*x*511/E/(E - x) + E*E*511*511/E/E/(E - x)/(E - x) + x*x/E/(E - x))
    else:
        return 0


def compton_all(x, peaks):
    """Compton function for all peaks."""
    y = 0
    for i in xrange(len(peaks)):
        y += compton(x, peaks[i][1], peaks[i][0])
    return y


# -------creating classes for errors in input file--------
def error_alert(message):
    """Popup error message window."""
    tkMessageBox.showwarning("Error", message)


class FormatError(Exception):
    """FormatError."""

    def __init__(self, name, must):
        """Init function."""
        self.name = name
        self.must = must

    def __str__(self):
        """Str method goes here."""
        error_alert("Incorrect format for %s  %s" % (self.name, self.must))
        return ("Incorrect format for %s  %s" % (self.name, self.must))


class SyntaxEntryError(Exception):
    """docstring for NameError."""

    def __init__(self, name):
        """Init function."""
        self.name = name

    def __str__(self):
        """Str method goes here."""
        error_alert("Incorrect syntax for %s " % self.name)
        return ("Incorrect syntax for %s " % self.name)


class PhysError(Exception):
    """docstring for LogicError."""

    def __init__(self, name, must):
        """Init function."""
        self.name = name
        self.must = must

    def __str__(self):
        """Str method goes here."""
        error_alert("Incorrect values for %s  %s" % (self.name, self.must))
        return ("Incorrect values for %s  %s" % (self.name, self.must))


class LenError(Exception):
    """docstring for LenError."""

    def __init__(self, name, n):
        """Init function."""
        self.name = name
        self.n = n

    def __str__(self):
        """Str method goes here."""
        error_alert("Incorrect parameters number for %s must be %i" % (self.name, self.n))
        return ("Incorrect parameters number for %s must be %i" % (self.name, self.n))


# --------creating functions to correct read data from file------
def correct_interval(energy_str):
    """Get correct energy interval from energy entrie."""
    try:
        interval = ast.literal_eval(energy_str)
    except (SyntaxError, ValueError) as error:
        raise SyntaxEntryError("'interval'")
    if type(interval) is not list:
        raise FormatError("'interval'", "must be '[Emin, Emax]'")
    if len(interval) != 2:
        raise LenError("'interval': "+str(interval), 2)
    if interval[0] >= interval[1]:
        raise PhysError("'interval'", "must be from min to max")
    if (interval[0] < 0 or interval[1] < 0):
        raise PhysError("'interval'", " Emin & Emax must be positive")
    return interval


def correct_peaks(peak_str, energy_str):
    """Get correct peaks parameter values from peak entrie."""
    try:
        peaks = ast.literal_eval(peak_str)[0]
    except (SyntaxError, ValueError) as error:
        raise SyntaxEntryError("'peaks'")
    interval = correct_interval(energy_str)
    if type(peaks) is not list:
        raise FormatError("'peaks'", "check format, please")
    for peak in peaks:
        if (len(peak) != 3):
            raise LenError("peak: "+str(peak), 3)
        for par in peak:
            t = str(type(par))[6:-1]
            try:
                float(par)
            except ValueError:
                raise FormatError("'peaks'", " invalid format %s in peak: %s" % (t, peak))
            if par < 0:
                raise PhysError("'peaks'", "parameters must be positive in peak: %s" % peak)
        if (peak[1] <= interval[0] or peak[1] >= interval[1]):
            raise PhysError("'peak': %s" % str(peak), "peak mean %1.2f is not in enegy interval" % float(peak[1]))
    return peaks


def correct_num_bin(bin_str):
    """Get correct bin numbers from num_bin entrie."""
    try:
        num_bin = ast.literal_eval(bin_str)
    except (SyntaxError, ValueError) as error:
        raise SyntaxEntryError("'num_bin'")
    t = str(type(num_bin))[6:-1]
    if (t != "'int'"):
        raise FormatError("'num_bin'", "'num_bin' must be int, not %s" % t)
    if num_bin <= 0:
        raise PhysError("'num_bin'", "'num_bin' must be >= 0")
    return num_bin


def correct_background(bg_str):
    """Get correct background parameters from background entrie."""
    try:
        background = ast.literal_eval(bg_str)
    except (SyntaxError, ValueError) as error:
        raise SyntaxEntryError("'background'")
    if type(background) is not list:
        raise FormatError("'background'", "must be '[a, b, c, d]'")
    if len(background) != 4:
        raise LenError("'background': "+str(background), 4)
    background[0] = math.log(background[0])
    return background


def correct_FWHM(FWHM_str):
    """Get correct FWHM parameters from FWHM entrie."""
    try:
        FWHM = ast.literal_eval(FWHM_str)
    except (SyntaxError, ValueError) as error:
        raise SyntaxEntryError("'FWHM_pars'")
    if type(FWHM) is not list:
        raise FormatError("'FWHM_pars'", "must be '[a0, a1]'")
    if len(FWHM) != 2:
        raise LenError("'FWHM_pars': "+str(), 2)
    return FWHM


def correct_option(input_dict):
    """Get correct opt1 parameter from dict."""
    try:
        opt1 = input_dict["opt1"]
    except (SyntaxError, ValueError) as error:
        raise SyntaxEntryError("'opt1'")
    t = str(type(opt1))[6:-1]
    if (t != "'int'"):
        raise FormatError("'opt1'", "'opt1' must be int, not %s" % t)
    if (opt1 != 1 and opt1 != 0):
        raise FormatError("'opt1' = %i" % opt1, "opt1 must be 0 or 1")
    return opt1


# -------------data entry------------
def file_to_dict(name):
    """Converct config file to python dict."""
    global load_var, load_label
    try:
        data_file = open(name, 'r')
        data_str = re.sub('<[^>]+>', '', data_file.read())
    except IOError as (errno, strerror):
        load_var.set("incorrect file:\n %s" % name)
        load_label.config(fg="red")
        print "I/O error({0}): {1}".format(errno, strerror)
        error_alert("I/O error({0}): {1}".format(errno, strerror))
        raise
    except:
        load_var.set("incorrect file:\n %s" % name)
        load_label.config(fg="red")
        print "Unknown Error", sys.exc_info()[0]
        error_alert("Unknown Error\n"+sys.exc_info()[0])
        raise
    try:
        data_dict = ast.literal_eval(data_str)
    except SyntaxError as (errno, strerror):
        load_var.set("incorrect file:\n %s" % name)
        load_label.config(fg="red")
        raise FormatError("line %s" % strerror[1], "")
        error_alert("Format Error\n" + sys.exc_info()[0])
        print "Format Error", sys.exc_info()[0]
        raise
    return data_dict


def get_data():
    """Get data from entries and return dict."""
    data_dict = {}
    peak_str = peak_entry.get('1.0', Tkinter.END).replace("]\n", "],")
    bg_str = bg_entry.get().replace("\n", "")
    bin_str = bin_entry.get().replace("\n", "")
    energy_str = energy_entry.get().replace("\n", "")
    FWHM_str = FWHM_entry.get().replace("\n", "")
    data_dict["interval"] = correct_interval(energy_str)
    data_dict["num_bin"] = correct_num_bin(bin_str)
    data_dict["peaks"] = correct_peaks(peak_str, energy_str)
    data_dict["opt1"] = opt_FWHM.get()
    data_dict["FWHM_pars"] = correct_FWHM(FWHM_str)
    data_dict["background"] = correct_background(bg_str)
    return data_dict


def set_data(data_dict):
    """Set data to entries."""
    clear_data()
    peak_entry.insert(1.0, str(data_dict["peaks"]).replace("],", "]\n"))
    energy_entry.insert(0, data_dict["interval"])
    bin_entry.insert(0, data_dict["num_bin"])
    bg_entry.insert(0, data_dict["background"])
    FWHM_entry.insert(0, data_dict["FWHM_pars"])
    opt_FWHM.set(data_dict["opt1"])


def clear_data():
    """Clears data in entries."""
    peak_entry.delete('1.0', Tkinter.END)
    energy_entry.delete(0, Tkinter.END)
    bin_entry.delete(0, Tkinter.END)
    bg_entry.delete(0, Tkinter.END)
    FWHM_entry.delete(0, Tkinter.END)


def set_default():
    """Set data from default dict to entries."""
    set_data(default_data_dict)


def save():
    """Save output files."""
    name = tkFileDialog.askdirectory(title="Enter path of directory that will creates for output files")
    if name == "":
        return
    else:
        data_dict = get_data()
        num_bin = data_dict['num_bin']
        label = name.split('/')[-1]
        global histograms, c1
        if (os.path.isdir(label+"_out") == 0):
            os.mkdir(label+"_out")
        for hist in histograms:
            n = hist.GetName()[4]
            c1.cd(int(n))
            ROOT.gPad.SaveAs(label+"_out"+"/"+label+"_"+n+".eps")
            output = []
            for i in xrange(num_bin-1):
                output += [[i+1, hist.GetBinContent(i+1)]]
            numpy.savetxt(label+"_out"+"/"+label+"_"+n+".txt",
                          output,
                          delimiter='     ',
                          fmt='%1i %1.3f')
            print "Info: txt file %s was created" % label + "_" + str(n)
            ROOT.gPad.Update()
            ROOT.gPad.Modified()
        return


def draw():
    """Draw histograms."""
    data_dict = get_data()
    global histograms
    histograms = main(data_dict)
    for hist in histograms:
        n = hist.GetName()[4]
        c1.cd(int(n))
        hist.SetMinimum(0)
        hist.Draw()
        ROOT.gPad.Update()
        ROOT.gPad.Modified()


def save_config():
    """Save configuration file from entries."""
    f = tkFileDialog.asksaveasfile(mode='w',
                                   defaultextension=".txt",
                                   title="Save config file as")
    if f is None:
        return
    text2save = str(get_data())
    f.write(text2save)
    f.close()


def load_file():
    """Set all data from file to entries."""
    file_name = tkFileDialog.Open(window,
                                  title="Open config file",
                                  filetypes=[('*.txt files', '.txt')]).show()
    if file_name == '':
        return
    load_var.set("opened file:\n %s" % file_name)
    load_label.config(fg="blue")
    data_dict = file_to_dict(file_name)
    clear_data()
    set_data(data_dict)
    return


def about():
    """Create about window."""
    global window, about_text
    about_window = Tkinter.Toplevel(window)
    about_window.geometry("550x480+0+0")
    about_window.title('About')
    Tkinter.Label(about_window, text=about_text).pack()


def help_f():
    """Create help window."""
    global window, help_text
    help_window = Tkinter.Toplevel(window)
    help_window.geometry("550x480+0+0")
    help_window.title('help')
    Tkinter.Label(help_window, text=help_text).pack()

def main(data_dict):
    """All calculating, hist creating goes here."""
    for i in xrange(4):
        if ROOT.gROOT.FindObject("hist%i" % (i+1)):
            ROOT.gROOT.FindObject("hist%i" % (i+1)).Delete()
    interval = data_dict["interval"]
    peaks = data_dict["peaks"]
    background = data_dict["background"]
    num_peaks = len(peaks)
    num_bin = data_dict["num_bin"]
    bin_width = (interval[1]-interval[0])/num_bin
    opt1 = data_dict["opt1"]
    FWHM_pars = data_dict["FWHM_pars"]
    c = 2.35482

    # ---------calculate Gauss heigth and FWHM-------
    H = []
    FWHM = []
    for i in xrange(num_peaks):
        if opt1 == 0:
            FWHM += [peaks[i][2]/c]
        else:
            FWHM += [FWHM_pars[0]+FWHM_pars[1]*math.sqrt(peaks[i][1])]
        H += [peaks[i][0]/(math.sqrt(2*math.pi)*FWHM[i])]

    # ----------write peks parameters in list--------
    parameters = []
    for i in xrange(num_peaks):
        for j in xrange(3):
            parameters += [peaks[i][j]]

    # --------convert intensity in Gauss height -------
    # --------and FWHM - in sigma----------
    for i in xrange(num_peaks):
        parameters[i*3] = H[i]
        parameters[3*i+2] = FWHM[i]

    # ------------creating 4 histograms---------------------
    hist1 = ROOT.TH1F("hist1", "delta", num_bin,
                      interval[0], interval[1])
    hist2 = ROOT.TH1F("hist2", "delta + background", num_bin,
                      interval[0], interval[1])
    hist3 = ROOT.TH1F("hist3", "gaus + background", num_bin,
                      interval[0], interval[1])
    histo = ROOT.TH1F("histo", "for calculation", num_bin,
                      interval[0], interval[1])
    hist4 = ROOT.TH1F("hist4", "gaus + background + random", num_bin,
                      interval[0], interval[1])
    back_func = ROOT.TF1("background", "expo(0) + pol1(2)",
                         interval[0], interval[1])
    back_func.SetParameters(background[0], background[1],
                            background[2], background[3])

    # ---------creating the func expression from all peaks--------
    all_peaks = "gaus(0)"
    for i in xrange(num_peaks-1):
        all_peaks += "+gaus"+"("+str((i+1)*3)+")"

    # -------creating func from all peaks--------------
    # -------set parameters---------------
    func = ROOT.TF1("all_peaks", all_peaks, interval[0], interval[1])
    for i in range(len(parameters)):
        func.SetParameter(i, parameters[i])

    # ------filling 1 histo with Delta-function-------
    for i in xrange(num_peaks):
        hist1.Fill(int(peaks[i][1]), peaks[i][0])
    # for i in xrange(num_bin-1):
    #     hist1.Fill(i+1, compton(i+1, peaks[0][1], peaks[0][0]))
    # ------filling 2 histo with Delta-function & Background+compton------
    for i in xrange(num_bin):
        x = i*bin_width+interval[0]
        hist2.SetBinContent(i+1, back_func(x) + compton_all(x, peaks))
    for i in xrange(num_peaks):
        hist2.Fill(peaks[i][1], peaks[i][0])

    # -------filling 3 histo with Gauss & Background-----------
    for i in xrange(num_bin):
        j = i*bin_width+interval[0]
        histo.SetBinContent(i+1, (func(j) + back_func(j) + compton_all(j, peaks)))
    # ------all bin i'ts a gauss ahhaha loool so we should ------
    # ------create gaus function for ich bin, and refil histo----
    # ------FWHM calculated for formula a0+a1*sqrt(E) by user parameters-----
    for i in xrange(num_bin):
        x = interval[0]
        fgaus = ROOT.TF1("fgaus", "gaus", interval[0], interval[1])
        sigma = math.sqrt(i * bin_width + interval[0]) * FWHM_pars[0] + FWHM_pars[1]
        ampli = histo.GetBinContent(i)/math.sqrt(2*3.141592)/sigma
        fgaus.SetParameters(ampli, i * bin_width+interval[0], sigma)

        for j in xrange(num_bin):
            hist3.SetBinContent(j, fgaus.Integral(x, x + bin_width)+hist3.GetBinContent(j))
            x = x + bin_width
    # ------filling 4 histo with Gauss & Background----
    # ------simulation statistical dispersion: --------
    # ------if counts in bin < 10-----
    # ------dispersion by Poisson, else - by Gauss
    for i in xrange(num_bin):
        y = hist3.GetBinContent(i)
        if y > 10:
            hist4.SetBinContent(i+1, ROOT.gRandom.Gaus(y, ROOT.TMath.Sqrt(y)))
        else:
            hist4.SetBinContent(i+1, ROOT.gRandom.Poisson(y))
    return [hist1, hist2, hist3, hist4]

# --------menu-------
menubar = Tkinter.Menu(window)
filemenu = Tkinter.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open config", command=load_file)
filemenu.add_command(label="Save config as ...", command=save_config)
filemenu.add_separator()
filemenu.add_command(label="Save output to ...", command=save)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Tkinter.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about)
helpmenu.add_command(label="Help", command=help_f)
menubar.add_cascade(label="Help", menu=helpmenu)


# -------setting up gui-------------
draw_btn = Tkinter.Button(window, bg="red", text=u"Draw", command=draw)
clear_btn = Tkinter.Button(window, bg="pink",
                           text=u"Clear All",
                           command=clear_data)
default_btn = Tkinter.Button(window, bg="white",
                             text=u"Set Default",
                             command=set_default)

peak_label.grid(row=1, column=1)
peak_entry.grid(row=2, column=1)
energy_label.grid(row=3, column=1)
energy_entry.grid(row=4, column=1)
bin_label.grid(row=5, column=1)
bin_entry.grid(row=6, column=1)
FWHM_check.grid(row=8, column=0)
FWHM_label.grid(row=8, column=1)
FWHM_entry.grid(row=9, column=1)
bg_label.grid(row=10, column=1)
bg_entry.grid(row=11, column=1)
load_label.config(fg='blue')
load_label.grid(row=0, column=1)
set_data(default_data_dict)

ROOT.gPad.Modified()
ROOT.gPad.Update()
draw_btn.grid(row=11, column=0)
clear_btn.grid(row=3, column=0)
default_btn.grid(row=2, column=0)
window.config(menu=menubar)
window.mainloop()
