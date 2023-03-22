from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from view.TridimensionalViewFrame import TridimensionalViewFrame
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from scipy import spatial
import threading
import segyio
import h5py
import numpy
import wx

class ImagePanel(wx.Panel):
    def __init__(self, parent, filename):
        super(ImagePanel, self).__init__(parent)

        # Definindo as variáveis que serão utilizadas
        self.volume = 0
        self.volumeInfo = None
        self.cmap = 'Greys'
        self.cmapSelect = None
        self.contrast = 2
        self.contrastInfo = None

        self.SetSize(parent.GetSize())

        # Criando a estrutura da imagem
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        # Executando o cube do segyio em outra thread
        print("~ Criando a imagem...")
        thread = threading.Thread(target=self.get_data, args=(filename,))
        thread.start()
        print('Carregando...')
        thread.join()

        #Iniciando a imagem no modo crossline
        self.on_select_crossline()
        print("~ Imagem criada!")

        # Sizer para o conteudo do painel
        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        self.sizer.Fit(self)
        self.SetSizer(self.sizer)

    
    def get_image_type_index(self):
        if (self.image_type == 'crossline'): return 0
        elif (self.image_type == 'inline'): return 1
        else: return 2


    def get_data(self, filename):
        if (filename.endswith('.segy') or filename.endswith('.sgy')):
            self.data = segyio.tools.cube(filename)
            self.std = self.data.std()
            self.filenameExtension = '.segy'

        elif (filename.endswith('.h5')):
            f = h5py.File(filename,'r')
            self.data = f['features']
            self.filenameExtension = '.h5'

        elif (filename.endswith('.npy')):
            self.data = numpy.load(filename)
            self.std = self.data.std()
            self.filenameExtension = '.npy'

        elif (filename.endswith('.xyz')):
            self.imagePanel = ImagePanelXYZ(self, filename)
            self.filenameExtension = '.xyz'


    def update_image_volume(self):
        if self.filenameExtension == '.h5':
            if self.image_type == 'crossline':
                self.sim.set_data(self.data[self.volume,:,:,0])
            elif self.image_type == 'inline':
                self.sim.set_data(self.data[:,self.volume,:,0])
            elif self.image_type == 'timeslice':
                self.sim.set_data(self.data[:,:,self.volume,0])

        elif self.filenameExtension == '.segy' or self.filenameExtension == '.npy':
            if self.image_type == 'crossline':
                self.sim.set_data(self.data[self.volume,:,:].T)
            elif self.image_type == 'inline':
                self.sim.set_data(self.data[:,self.volume,:].T)
            elif self.image_type == 'timeslice':
                self.sim.set_data(self.data[:,:,self.volume].T)

        self.canvas.draw()


    def update_image_cmap(self):
        self.sim.set_cmap(self.cmap)
        self.canvas.draw()


    def update_image_contrast(self):
        if self.filenameExtension == '.h5':
            ...

        elif self.filenameExtension == '.segy' or self.filenameExtension == '.npy':
            min = -1 * self.contrast
            max = self.contrast
            self.sim.set_clim(vmin = min * self.std, vmax = max * self.std)
            self.canvas.draw()


    # Ao mudar o valor do scroll
    def on_slider_scroll(self, e):
        obj = e.GetEventObject()
        val = obj.GetValue()
        self.volume = val
        self.volumeInfo.SetLabel(str(val))
        self.update_image_volume()


    # Ao selecionar Imagem > Volume
    def on_select_volume(self, e):
        dialog = wx.Dialog(self, 1, "Alterar volume da sísmica", size=(400,100))

        # Criando o slider
        sizer = wx.GridBagSizer(5, 5)
        slider = wx.Slider(dialog, value=self.volume, minValue=0, maxValue=self.axis_size-1, style=wx.SL_HORIZONTAL)

        # Bindando o evento de scroll
        slider.Bind(wx.EVT_SCROLL, self.on_slider_scroll)
    
        # Adicionando o slider ao dialog
        sizer.Add(slider, pos=(0, 0), flag=wx.ALL|wx.EXPAND, border=25)

        # Adicionando texto de valor do volume
        self.volumeInfo = wx.StaticText(dialog, label=str(self.volume))
        sizer.Add(self.volumeInfo, pos=(0, 1), flag=wx.TOP|wx.RIGHT, border=25)

        sizer.AddGrowableCol(0)
        dialog.SetSizer(sizer)

        dialog.ShowModal()


    # Ao selecionar Imagem > Mapa de Cores
    def on_change_cmap(self, e):
        self.cmap = self.cmapSelect.GetStringSelection()
        self.update_image_cmap()


    def on_select_cmap(self, e):
        dialog = wx.Dialog(self, 1, "Alterar mapa de cores da imagem", size=(300,150))
        sizer = wx.GridBagSizer(5, 5)
        cmaps = ["Greys", "seismic", "Accent", "terrain"]

        # Select dos cmap's disponíveis
        self.cmapSelect = wx.Choice(dialog, choices=cmaps)
        self.cmapSelect.SetStringSelection(self.cmap)
        self.cmapSelect.Bind(wx.EVT_CHOICE, self.on_change_cmap)
        sizer.Add(self.cmapSelect, pos=(0,0), flag=wx.EXPAND | wx.ALL, border=10)

        sizer.AddGrowableCol(0)
        dialog.SetSizer(sizer)

        dialog.ShowModal()


    # Ao mudar o valor do scroll de contraste
    def on_contrast_slider_scroll(self, e):
        obj = e.GetEventObject()
        val = obj.GetValue()
        self.contrast = val
        self.contrastInfo.SetLabel(str(val))
        self.update_image_contrast()


    # Ao selecionar Imagem > Contraste
    def on_select_contrast(self, e):
        dialog = wx.Dialog(self, 1, "Alterar contraste da imagem", size=(400,100))

        # Criando o slider
        sizer = wx.GridBagSizer(5, 5)
        slider = wx.Slider(dialog, value=self.contrast, minValue=1, maxValue=2, style=wx.SL_HORIZONTAL)

        # Bindando o evento de scroll
        slider.Bind(wx.EVT_SCROLL, self.on_contrast_slider_scroll)
    
        # Adicionando o slider ao dialog
        sizer.Add(slider, pos=(0, 0), flag=wx.ALL|wx.EXPAND, border=25)

        # Adicionando texto de valor do contraste
        self.contrastInfo = wx.StaticText(dialog, label=str(self.contrast))
        sizer.Add(self.contrastInfo, pos=(0, 1), flag=wx.TOP|wx.RIGHT, border=25)

        sizer.AddGrowableCol(0)
        dialog.SetSizer(sizer)

        dialog.ShowModal()


    # Ao selecionar Imagem > Similaridade
    def on_select_similarity(self, e):
        dialog = wx.Dialog(self, 2, "Similaridade entre os slices", size=(500,550))
        sizer = wx.BoxSizer(wx.VERTICAL)

        current_image = self.sim.get_array().flatten()
        similarity = []
        x = []
        index = self.get_image_type_index()

        for i in range(self.data.shape[index]):
            x.append(i)

            match index:
                case 0: i_image = self.data[i,:,:].T.flatten()
                case 1: i_image = self.data[:,i,:].T.flatten()
                case 2: i_image = self.data[:,:,i].T.flatten()
            
            result = 1 - spatial.distance.cosine(current_image, i_image)
            similarity.append(result)

        figure = Figure(figsize=(5,5))
        axes = figure.add_subplot(111)
        axes.plot(x, similarity)
        canvas = FigureCanvas(dialog, 2, figure)

        sizer.Add(canvas)
        dialog.SetSizer(sizer)
        canvas.draw()

        dialog.ShowModal()


    def on_select_3D_view(self, e):
        TridimensionalViewFrame(self.data)


    def on_select_crossline(self, e=None):
        self.image_type = 'crossline'
        self.axis_size = self.data.shape[0]
        if self.filenameExtension == '.h5':
            self.sim = self.axes.imshow(self.data[self.volume,:,:,0], cmap = self.cmap)
        elif self.filenameExtension == '.segy' or self.filenameExtension == '.npy':
            self.sim = self.axes.imshow(self.data[self.volume,:,:].T, vmin = -2 * self.std, vmax = 2 * self.std, cmap = self.cmap)
        self.canvas.draw()


    def on_select_inline(self, e=None):
        self.image_type = 'inline'
        self.axis_size = self.data.shape[1]
        if self.filenameExtension == '.h5':
            self.sim = self.axes.imshow(self.data[:,self.volume,:,0], cmap = self.cmap)
        elif self.filenameExtension == '.segy' or self.filenameExtension == '.npy':
            self.sim = self.axes.imshow(self.data[:,self.volume,:].T, vmin = -2 * self.std, vmax = 2 * self.std, cmap = self.cmap)
        self.canvas.draw()


    def on_select_timeslice(self, e=None):
        self.image_type = 'timeslice'
        self.axis_size = self.data.shape[2]
        if self.filenameExtension == '.h5':
            self.sim = self.axes.imshow(self.data[:,:,self.volume,0], cmap = self.cmap)
        elif self.filenameExtension == '.segy' or self.filenameExtension == '.npy':
            self.sim = self.axes.imshow(self.data[:,:,self.volume].T, vmin = -2 * self.std, vmax = 2 * self.std, cmap = self.cmap)
        self.canvas.draw()
