import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
from datetime import datetime

class AppVendas:
    def __init__(self, root):
        self.root = root
        self.root.title("App de Vendas")

        self.produtos = []
        self.subtotais = []  # Lista para armazenar os subtotais

        self.carregar_produtos()

        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        menu_cadastro = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Cadastro", menu=menu_cadastro)
        menu_cadastro.add_command(label="Cadastro de Produtos", command=self.cadastro_produtos)

        self.produto_combobox = ttk.Combobox(root, state="readonly", width=30)
        self.produto_combobox.grid(row=0, column=1, padx=20, pady=10)

        frame_cadastro_vendas = tk.LabelFrame(root, text="Cadastro de Vendas")
        frame_cadastro_vendas.grid(row=1, column=0, columnspan=2, padx=20, pady=10)

        tk.Label(frame_cadastro_vendas, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.produto_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.produto_combobox.bind("<<ComboboxSelected>>", self.atualizar_valor_produto)

        tk.Label(frame_cadastro_vendas, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5)
        self.quantidade_entry = tk.Entry(frame_cadastro_vendas, width=10)
        self.quantidade_entry.grid(row=1, column=1, padx=5, pady=5)
        self.quantidade_entry.insert(0, "1")

        tk.Label(frame_cadastro_vendas, text="Valor:").grid(row=2, column=0, padx=5, pady=5)
        self.valor_entry = tk.Entry(frame_cadastro_vendas, width=10, state="readonly")
        self.valor_entry.grid(row=2, column=1, padx=5, pady=5)

        cadastrar_btn = tk.Button(frame_cadastro_vendas, text="Cadastrar Venda", command=self.cadastrar_venda)
        cadastrar_btn.grid(row=3, columnspan=2, padx=5, pady=10)

        frame_vendas = tk.LabelFrame(root, text="Registro de Vendas")
        frame_vendas.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

        self.tree = ttk.Treeview(frame_vendas, columns=("Produto", "Quantidade", "Subtotal"), show="headings")
        self.tree.heading("#0", text="ID", anchor=tk.CENTER)
        self.tree.heading("Produto", text="Produto", anchor=tk.CENTER)
        self.tree.heading("Quantidade", text="Quantidade", anchor=tk.CENTER)
        self.tree.heading("Subtotal", text="Subtotal", anchor=tk.CENTER)
        self.tree.pack(fill="both", expand=True)

        self.label_total_vendas = tk.Label(root, text="Total de Vendas: 0")
        self.label_total_vendas.grid(row=3, column=0, padx=20, pady=5)

        self.label_total_arrecadado = tk.Label(root, text="Total Arrecadado: R$ 0.00")
        self.label_total_arrecadado.grid(row=3, column=1, padx=20, pady=5)

        self.atualizar_combobox_produtos()
        self.carregar_registro_vendas()

    def cadastro_produtos(self):
        cadastro_produtos_window = tk.Toplevel(self.root)
        cadastro_produtos_window.title("Cadastro de Produtos")

        tk.Label(cadastro_produtos_window, text="Nome do Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.nome_produto_entry = tk.Entry(cadastro_produtos_window)
        self.nome_produto_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(cadastro_produtos_window, text="Preço:").grid(row=1, column=0, padx=5, pady=5)
        self.preco_produto_entry = tk.Entry(cadastro_produtos_window)
        self.preco_produto_entry.grid(row=1, column=1, padx=5, pady=5)

        cadastrar_produto_btn = tk.Button(cadastro_produtos_window, text="Cadastrar Produto", command=self.cadastrar_produto)
        cadastrar_produto_btn.grid(row=2, columnspan=2, padx=5, pady=10)

    def cadastrar_produto(self):
        nome = self.nome_produto_entry.get()
        preco = self.preco_produto_entry.get()

        if nome and preco:
            preco = float(preco)
            produto = {
                'nome': nome,
                'preco': preco
            }
            self.produtos.append(produto)

            self.atualizar_combobox_produtos()

            self.salvar_produtos()

            self.nome_produto_entry.delete(0, tk.END)
            self.preco_produto_entry.delete(0, tk.END)

            messagebox.showinfo("Sucesso", f"Produto '{nome}' cadastrado com sucesso!")
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

    def atualizar_combobox_produtos(self):
        self.produto_combobox['values'] = []
        nomes_produtos = [produto['nome'] for produto in self.produtos]
        self.produto_combobox['values'] = nomes_produtos

    def atualizar_valor_produto(self, event):
        nome_produto = self.produto_combobox.get()

        if nome_produto:
            preco_produto = next((produto['preco'] for produto in self.produtos if produto['nome'] == nome_produto), None)

            if preco_produto is not None:
                self.valor_entry.config(state="normal")
                self.valor_entry.delete(0, tk.END)
                self.valor_entry.insert(0, f"{preco_produto:.2f}")
                self.valor_entry.config(state="readonly")

    def cadastrar_venda(self):
        nome_produto = self.produto_combobox.get()
        quantidade = self.quantidade_entry.get()

        if nome_produto and quantidade:
            quantidade = int(quantidade)
            preco_produto = next((produto['preco'] for produto in self.produtos if produto['nome'] == nome_produto), None)

            if preco_produto is not None:
                subtotal = preco_produto * quantidade

                self.tree.insert("", tk.END, values=(nome_produto, quantidade, subtotal))
                self.subtotais.append(subtotal)  # Adiciona o subtotal à lista

                total_vendas = len(self.tree.get_children())
                self.label_total_vendas.config(text=f"Total de Vendas: {total_vendas}")

                total_arrecadado = sum(self.subtotais)
                self.label_total_arrecadado.config(text=f"Total Arrecadado: R$ {total_arrecadado:.2f}")

                # Log da venda
                self.log_venda(nome_produto, quantidade, subtotal)

                self.produto_combobox.set('')
                self.quantidade_entry.delete(0, tk.END)
                self.quantidade_entry.insert(0, "1")

                #messagebox.showinfo("Sucesso", "Venda cadastrada com sucesso!")
            else:
                messagebox.showerror("Erro", "Produto não encontrado.")
        else:
            messagebox.showerror("Erro", "Por favor, selecione um produto e informe uma quantidade válida.")

    def log_venda(self, nome_produto, quantidade, subtotal):
        try:
            data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{data_hora} - Produto: {nome_produto}, Quantidade: {quantidade}, Subtotal: {subtotal}\n"

            with open("registro_vendas.txt", "a") as f:
                f.write(log_entry)
        except Exception as e:
            messagebox.showerror("Erro ao registrar venda", f"Ocorreu um erro ao registrar a venda: {str(e)}")

    def salvar_produtos(self):
        try:
            with open("produtos.json", "w") as f:
                json.dump(self.produtos, f, indent=4)
        except Exception as e:
            messagebox.showerror("Erro ao salvar produtos", f"Ocorreu um erro ao salvar os produtos: {str(e)}")

    def carregar_produtos(self):
        try:
            with open("produtos.json", "r") as f:
                self.produtos = json.load(f)
        except FileNotFoundError:
            self.salvar_produtos()
        except json.JSONDecodeError:
            messagebox.showwarning("Aviso", "Arquivo de produtos está vazio ou mal formatado.")

    def carregar_registro_vendas(self):
        try:
            with open("registro_vendas.txt", "r") as f:
                for line in f:
                    # Exemplo de linha do arquivo: "2024-07-13 15:30:00 - Produto: Produto1, Quantidade: 2, Subtotal: 20.00\n"
                    data_hora, venda_info = line.split(' - ')
                    produto_info = venda_info.split(', ')
                    nome_produto = produto_info[0].split(': ')[1]
                    quantidade = int(produto_info[1].split(': ')[1])
                    subtotal = float(produto_info[2].split(': ')[1])

                    self.tree.insert("", tk.END, values=(nome_produto, quantidade, subtotal))
                    self.subtotais.append(subtotal)

            total_vendas = len(self.tree.get_children())
            self.label_total_vendas.config(text=f"Total de Vendas: {total_vendas}")

            total_arrecadado = sum(self.subtotais)
            self.label_total_arrecadado.config(text=f"Total Arrecadado: R$ {total_arrecadado:.2f}")

        except FileNotFoundError:
            messagebox.showwarning("Aviso", "Arquivo de registro de vendas não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro ao carregar registro de vendas", f"Ocorreu um erro ao carregar o registro de vendas: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppVendas(root)
    root.mainloop()
