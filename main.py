import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.clock import Clock
from binance import Client
import decimal, math
import warnings, os
warnings.filterwarnings('ignore')

class ScreenOne(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class Grafico(Image):
    pass

class MainApp(MDApp):
    saldo_money=1000
    saldo_monedas=0
    status=''
    ultimo_precio=1
    sma_20_anterior=1
    precio_anterior=1
    df = pd.DataFrame([])
    precision=5

    def build(self):
        self.token='BTCUSDT'
        self.api_key='YhOJXxZqbaP7PzuXwdNNxMbXLpyuDrMAFmuonp7qvuWpxYhMPOvZr08gHGlD2F7I'
        self.api_secret='16qZzduO2JV7L1nGtyO0OidcGl1QJXABWv7vUaBVN9Oiyi5FAp5OpoKGdq1KNJAZ'
        self.client = Client(self.api_key, self.api_secret)
        self.grafico1 = self.root.get_screen('first').ids.graf1
        self.ejecutar(0)
        #Clock.schedule_interval(self.ejecutar, 3600)   

    def ejecutar(self, tiempo):
        self.cargar_ordenes()
        self.simular() #Cambiar por self.comprar() para ejecutarlo con Binance
        self.visualizar()

    def cargar_ordenes(self):      
        start = pd.to_datetime(dt.datetime.now() - pd.Timedelta(days = 60))
        end = dt.datetime.now()
        interval = '1h'

        klines = self.client.get_historical_klines(str(self.token), interval, int(dt.datetime.timestamp(start) * 1000), int(dt.datetime.timestamp(end) * 1000), limit=1000)
        self.df_order = pd.DataFrame(klines)
        self.df_order.columns = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore']
        self.df_order['Date'] = pd.to_datetime(self.df_order.OpenTime, unit='ms')
        self.df_order['Close'] = self.df_order['Close'].apply(lambda x: float(x))
        self.df_order['SMA_20'] = self.df_order['Close'].rolling(window = 20).mean()
        minimo = self.df_order['Close'][0]
        maximo = self.df_order['Close'][0]
        for index, row in self.df_order.sort_values(by=['Date'], ascending=True).iterrows():
            minimo = (row['Close'] if row['Close'] < minimo else minimo)
            maximo = (row['Close'] if row['Close'] > maximo else maximo)
            self.df_order.at[index, 'Minimo'] = minimo
            self.df_order.at[index, 'Maximo'] = maximo
        self.df_order = self.df_order[['Date', 'Close', 'Minimo', 'Maximo', 'SMA_20']]
        print(self.df_order.tail())

    def compra_venta(self):
        self.saldo_money, self.monedas = self.devolver_balances()
        fecha = self.df_order['Date'].iloc[-1]
        precio = self.df_order['Close'].iloc[-1]
        self.precio_anterior = self.df_order['Close'].iloc[-2]
        minimo = self.df_order['Minimo'].iloc[-1]
        maximo = self.df_order['Maximo'].iloc[-1]
        sma_20 = self.df_order['SMA_20'].iloc[-1]
        self.sma_20_anterior = self.df_order['SMA_20'].iloc[-2]     
        media = (minimo+maximo)/2
        baja = True if (maximo/minimo>1.1 and precio/media<0.965) else False

        if (self.status == '' or self.status == 'venta') and int(self.saldo_money) > 0:
            if ((precio<(minimo+media)/2 and baja==False)
                or 
                (baja==True and precio/minimo<1.05 and precio>self.precio_anterior and sma_20>self.sma_20_anterior)):
                coins = self.truncate((self.saldo_money / precio)*0.99, self.precision)
                order = self.client.create_order(symbol=self.token, side='BUY', type='MARKET', quantity=coins)
                self.status = 'compra'
                self.ultimo_precio = precio
                self.saldo_money = 0
                self.monedas = coins
                new_row = {'Date': fecha, 'Close': precio, 'Ultimo_Status': self.status, 'Ultimo_Precio':self.ultimo_precio}
                self.df = self.df.append(new_row, ignore_index=True)
        elif self.status == 'compra' and self.monedas > 0:
            if ((baja==False and (precio > media) and (sma_20/self.sma_20_anterior>1.002) and (precio/self.precio_anterior>1.002))
                or
                (baja==True and precio/self.ultimo_precio>1.01)):
                coins = self.truncate(self.monedas, self.precision)
                order = self.client.create_order(symbol = self.token, side='SELL', type = 'MARKET', quantity=coins)
                self.status = 'venta'
                self.ultimo_precio = precio
                self.saldo_money = coins*precio
                self.monedas = 0
                new_row = {'Date': fecha, 'Close': precio, 'Ultimo_Status': self.status, 'Ultimo_Precio':self.ultimo_precio}
                self.df = self.df.append(new_row, ignore_index=True)

    def simular(self):
        for index, row in self.df_order.sort_values(by=['Date'], ascending=True).iterrows():
            fecha = row['Date']
            precio = row['Close']
            minimo = row['Minimo']
            maximo = row['Maximo']
            media = (minimo+maximo)/2
            sma_20 = row['SMA_20']
            baja = True if (maximo/minimo>1.1 and precio/media<0.965) else False
            if (self.status == '' or self.status == 'venta') and int(self.saldo_money) > 0:
                if ((baja==False and precio<(minimo+media)/2)
                    or
                    (baja==True and precio/minimo<1.05 and precio>self.precio_anterior and sma_20>self.sma_20_anterior)
                    ):
                    coins = self.truncate((self.saldo_money/precio)*0.99, self.precision)
                    self.status='compra'
                    self.ultimo_precio = precio
                    self.saldo_money=0
                    self.monedas = coins
                    new_row = {'Date': fecha, 'Close': precio, 'Ultimo_Status':self.status, 'Ultimo_Precio': self.ultimo_precio}
                    self.df = self.df.append(new_row, ignore_index=True)                
            elif self.status == 'compra' and self.monedas > 0:
                if ((baja==False and (precio>media) and (sma_20/self.sma_20_anterior>1.002) and (precio/self.precio_anterior>1.002))
                    or
                    (baja==True and precio/self.ultimo_precio>1.01)
                    ):
                    self.status='venta'
                    self.ultimo_precio = precio
                    self.saldo_money=coins*precio
                    self.monedas = 0
                    new_row = {'Date': fecha, 'Close': precio, 'Ultimo_Status':self.status, 'Ultimo_Precio': self.ultimo_precio}
                    self.df = self.df.append(new_row, ignore_index=True)
            self.sma_20_anterior = sma_20
            self.precio_anterior = precio
        if self.status == 'compra':
            self.saldo_money = coins*precio

    def visualizar(self):
        if os.path.exists("grafico1.png"): os.remove("grafico1.png")
        grafico = self.df
        if len(grafico)>0:                
            grafico['Date'] = grafico['Date'].astype('datetime64[ns]')
            grafico['Buy_Signal'] = np.where(grafico['Ultimo_Status'] == 'compra', grafico['Ultimo_Precio'], np.nan)
            grafico['Sell_Signal'] = np.where(grafico['Ultimo_Status'] == 'venta', grafico['Ultimo_Precio'], np.nan)
            grafico = grafico[['Date', 'Close', 'Buy_Signal', 'Sell_Signal']]

        data = self.df_order
        data['Buy_Signal'] = np.nan 
        data['Sell_Signal'] = np.nan 
        data = data[['Date', 'Close', 'Buy_Signal', 'Sell_Signal']]

        graph = pd.concat([grafico, data], ignore_index=True)
        graph = graph.sort_values(by=['Date'], ascending=True)      
        graph = graph.set_index(pd.DatetimeIndex(graph['Date'].values))

        # Personalizar gráfico
        titulo = str(self.token) + ' - Precio y Señales de Compra y Venta'
        plt.clf()
        plt.figure(figsize=(22,7))                    
        plt.title(titulo, loc='left', fontsize=22, color='#607d8b', fontweight="bold", pad = 30)
        plt.plot(graph.index, graph['Close'], label='Precio del Dia', alpha = 0.8)
        plt.plot(graph.index, graph['Buy_Signal'], color='green', label='Compra', marker='^', alpha=1, markersize=10)
        plt.plot(graph.index, graph['Sell_Signal'], color='red', label='Venta', marker='v', alpha=1, markersize=10)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel('Fecha', color='#607d8b', fontsize=20)
        plt.ylabel('Precio del Dia', color='#607d8b', fontsize=20)
        plt.annotate('$Saldo = {0:.0f}$'.format(round(self.saldo_money,0)), xy=(0.88, 0.72), xycoords='axes fraction', fontsize=20)
        plt.legend(loc='best', fontsize=15)
        p = plt.gcf()
        
        # Adicionando gráfico a Kivy
        p.savefig('grafico1.png',bbox_inches='tight')      
        plt.close('all')
        self.grafico1.source = 'grafico1.png'
        self.grafico1.reload()

    def devolver_balances(self):        
        balance = self.client.get_asset_balance(asset='BRL')
        if balance:
            saldo_money = float(balance.get('free'))
        else:
            saldo_money = 0

        balance = self.client.get_asset_balance(asset=self.token.replace("BRL", ""))
        if balance:
            monedas = float(balance.get('free'))
        else:
            monedas = 0            

        return saldo_money, monedas

    def truncate(self, number, decimals=0):
        if decimals == 0: return math.trunc(number)
        factor = 10.0 ** decimals
        return math.trunc(number * factor) / factor

MainApp().run()