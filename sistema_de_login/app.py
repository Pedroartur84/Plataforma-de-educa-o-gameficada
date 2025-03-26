import customtkinter as ctk
from PIL import Image # para caregar imagens com o pillow
from tkinter import PhotoImage


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configuracaoes_da_janela_inicial()
        self.tela_de_login()
    
    #configurando a janela principal  
    def configuracaoes_da_janela_inicial(self):
        self.geometry("700x400")
        self.title("sistema de login")
        self.resizable(False, False)
      
    def tela_de_login(self):
        try:
            self.img = ctk.CTkImage(
                light_image=Image.open("C:\\Users\\pdat5\\artur.dev\\Plataforma_EAD_Gameficada\\sistema_de_login\\logi-img.png"),#caminho
                size=(330, 345)#ajuste de tamanho
            )
        except FileNotFoundError:
            print("arquivo de imagen não encontrado")
            return
        self.lb_img = ctk.CTkLabel(self, text=None, image=self.img)
        self.lb_img.grid(row=1, column=0, padx=10)
        #trabalhando com imagens
        
        #titulo da plataforma
        self.title = ctk.CTkLabel(self, text="faça o seu login \n ou cadastre-se! ", font=("century gothic bold", 14))
        self.title.grid(row=1, column=0, pady=10, padx=10)
        
        #criar a frame do formulario de login
        self.frame_login = ctk.CTkFrame(self, width=350, height=380)
        self.frame_login.place(x=350, y=10)
        
        #colocando widgets dentro do frame - formulario de login
        self.lb_title = ctk.CTkLabel (self.frame_login, text="faça seu login".upper(), font=("century gothic bold", 22))
        self.lb_title.grid (row=0, column=0, padx=10, pady=10)
        
        # Area para colocar o nome do usuario
        self.username_login_entry = ctk.CTkEntry (self.frame_login, width=300, placeholder_text="seu nome de usuario..", font=("century gothic bold", 16), corner_radius=15, border_color="blue")
        self.username_login_entry.grid (row=1, column=0, pady=10, padx=10)
        
        # Area para colocar a senha do usuario
        self.senha_login_entry = ctk.CTkEntry (self.frame_login, width=300, placeholder_text="sua senha de usuario..", font=("century gothic bold", 16), corner_radius=15, border_color="blue")
        self.senha_login_entry.grid (row=2, column=0, pady=10, padx=10)
        
        # Botão para ver senha
        self.ver_senha = ctk.CTkCheckBox (self.frame_login, text="clique para ver a senha" , font=("century gothic bold", 12), corner_radius=15, border_color="blue")
        self.ver_senha.grid (row=3, column=0, pady=10, padx=10)
        
        # Botão de fazer login
        self.btn_login = ctk.CTkButton (self.frame_login, width=300, text="fazer login".lower(), font=("century gothic bold", 16), corner_radius=15)
        self.btn_login.grid (row=4, column=0, pady=10, padx=10)
        
        # spam para caso não tenha uma conta
        self.spam = ctk.CTkLabel(self.frame_login, text=" Não tenho uma conta! ", font=("century gothic bold", 12))
        self.spam.grid (row=5, column=0, pady=10, padx=10)
        
        # Botão para caso não tenha uma conta
        self.btn_cadastro = ctk.CTkButton (self.frame_login, width=300, text="fazer cadastro".lower(), font=("century gothic bold", 16), corner_radius=15)
        self.btn_cadastro.grid (row=6, column=0, pady=10, padx=10)
        
if __name__=="__main__":
    App = App()
    App.mainloop()