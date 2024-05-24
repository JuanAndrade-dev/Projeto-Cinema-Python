import string
import sqlite3
import getpass
def criar_tabela_alimentos(cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS alimentos
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL)''')
def criar_tabela_bebidas(cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS bebidas
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL)''')
def criar_tabela_usuarios(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome TEXT NOT NULL,
                       senha TEXT NOT NULL,
                       admin INTEGER NOT NULL)''')

def criar_tabela_filmes(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS filmes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       titulo TEXT NOT NULL,
                       sinopse TEXT)''')


def criar_tabela_precos(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS precos
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       filme_id INTEGER NOT NULL,
                       preco REAL NOT NULL,
                       UNIQUE (filme_id, preco),
                       FOREIGN KEY (filme_id) REFERENCES filmes(id))''')

def criar_tabela_sessoes(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessoes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       filme_id INTEGER NOT NULL,
                       horario TEXT NOT NULL,
                       dublado INTEGER NOT NULL,
                         sinopse TEXT,
                       FOREIGN KEY (filme_id) REFERENCES filmes(id))''')
  
def inserir_usuarios_admin(cursor):
    cursor.execute('''INSERT INTO usuarios (nome, senha, admin) VALUES (?, ?, ?)''', ('argemito', 'lagostinha', 1))
    cursor.execute('''INSERT INTO usuarios (nome, senha, admin) VALUES (?, ?, ?)''', ('calvao', '1234', 1))

def main():
    num_fileiras = 24
    num_assentos = 6
    sala_de_cinema = [["disponível" for _ in range(num_assentos)] for _ in range(num_fileiras)]

    conn = sqlite3.connect('prima.sql')  
    cursor = conn.cursor()


    
    criar_tabela_usuarios(cursor)
    criar_tabela_filmes(cursor)
    criar_tabela_precos(cursor)
    criar_tabela_sessoes(cursor)
    criar_tabela_alimentos(cursor)
    criar_tabela_bebidas(cursor)

    
    # Inserção dos usuários admin
    inserir_usuarios_admin(cursor)
    
    conn.commit()

    while True:
        print("Bem-vindo ao sistema de cinema!")
        opcao = input("Digite 'iniciar' para começar, 'sair' para sair: ")

        if opcao.lower() == 'bananinha':
            usuario = input("Digite o nome de usuário: ")
            senha = getpass.getpass("Digite a senha: ")
            if autenticar_usuario(cursor, usuario, senha):
                acesso_admin(cursor, conn)
            else:
                print("Acesso negado. Nome de usuário ou senha incorretos.")
        elif opcao == 'iniciar':
            acesso_usuario(cursor, sala_de_cinema)
        elif opcao == 'sair':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

def autenticar_usuario(cursor, usuario, senha):
    cursor.execute("SELECT nome, senha FROM usuarios WHERE nome = ? AND senha = ?", (usuario, senha))
    return cursor.fetchone() is not None

def acesso_usuario(cursor, sala_de_cinema):
    while True:
        catalogo_filmes = obter_catalogo(cursor)
        print("Filmes disponíveis:")
        for i, filme in enumerate(catalogo_filmes, 1):
            print(f"{i}. {filme[1]} - Preço: R${filme[2]:.2f}")
        
        escolha_filme = input("Escolha o filme que deseja assistir, digite 'sair' para sair do catálogo: ")
        
        if escolha_filme == 'sair':
            print("Saindo...")
            break
        
        if escolha_filme.isdigit() and 1 <= int(escolha_filme) <= len(catalogo_filmes):
            filme_escolhido = catalogo_filmes[int(escolha_filme) - 1]
            print(f"Você escolheu assistir a '{filme_escolhido[1]}'")
            preco_ingresso = filme_escolhido[2]
            
            while True:
                quantidade_ingressos = int(input("Digite a quantidade de ingressos desejada (ou digite 0 para voltar ao catálogo): "))
                if quantidade_ingressos == 0:
                    break
                total = preco_ingresso * quantidade_ingressos
                print(f"Total a pagar: R${total:.2f}")

                horario_sessao = escolher_horario(cursor, filme_escolhido[0])
                dublado = input("Digite 'dublado' para dublado ou 'legendado' para legendado: ").lower()
                if dublado not in ('dublado', 'legendado'):
                    print("Opção inválida. Escolha 'dublado' ou 'legendado'.")
                    continue
                print()
                recibo = selecionar_cadeiras(sala_de_cinema, quantidade_ingressos, filme_escolhido[0], horario_sessao, dublado)
                nome_completo = input("Digite seu nome completo: ")
                cpf = input("Digite seu CPF: ")
                exibir_recibo(nome_completo, cpf, filme_escolhido[1], horario_sessao, recibo, total)
                print()
                break
        else:
            print("Opção inválida.")

def obter_catalogo(cursor):
    cursor.execute("SELECT filmes.id, filmes.titulo, COALESCE(avg(precos.preco), 0) AS preco FROM filmes LEFT JOIN precos ON filmes.id = precos.filme_id GROUP BY filmes.id, filmes.titulo")
    return cursor.fetchall()

def adicionar_filme(cursor, titulo):
    cursor.execute("INSERT INTO filmes (titulo) VALUES (?)", (titulo,))
    
def remover_filme(cursor, titulo):
    cursor.execute("DELETE FROM filmes WHERE titulo = ?", (titulo,))
    
def definir_preco(cursor, filme_id, preco):
    cursor.execute("INSERT OR REPLACE INTO precos (filme_id, preco) VALUES (?, ?)", (filme_id, preco))

def adicionar_sessao(cursor, filme_id, horario, dublado, sinopse=""):
    cursor.execute("INSERT INTO sessoes (filme_id, horario, dublado, sinopse) VALUES (?, ?, ?, ?)", (filme_id, horario, dublado, sinopse))
    cursor.execute("UPDATE filmes SET sinopse = ? WHERE id = ?", (sinopse, filme_id))
    cursor.connection.commit()

def escolher_horario(cursor, filme_id):
    print("Horários disponíveis para esta sessão:")
    horarios = obter_horarios(cursor, filme_id)
    for i, horario in enumerate(horarios, 1):
        dublado = "Dublado" if horario[1] == "dublado" else "Legendado"
        print(f"{i}. {horario[0]} ({dublado})")

    escolha_horario = input("Escolha o horário da sessão (ou digite 0 para voltar ao catálogo): ")

    if escolha_horario == '0':
        return None

    if escolha_horario.isdigit() and 1 <= int(escolha_horario) <= len(horarios):
        return horarios[int(escolha_horario) - 1][0]
    else:
        print("Opção inválida. Escolha um dos horários disponíveis.")
        return escolher_horario(cursor, filme_id)

def obter_horarios(cursor, filme_id):
    cursor.execute("SELECT horario, dublado FROM sessoes WHERE filme_id = ?", (filme_id,))
    return cursor.fetchall()

def selecionar_cadeiras(sala_de_cinema, quantidade_ingressos, filme_id, horario_sessao, dublado):
    letras_fileiras = string.ascii_uppercase[:len(sala_de_cinema)]
    recibo = []

    while quantidade_ingressos > 0:
        mostrar_cadeiras(sala_de_cinema)
        entrada = input("Digite a letra da fileira e o número do assento (exemplo: A1) ou '0' para voltar ao catálogo: ")
        
        if entrada == '0':
            return recibo
        
        if len(entrada) != 2:
            print("Entrada inválida. Use o formato correto (exemplo: A1).")
            continue
        
        letra_fileira = entrada[0].upper()
        numero_assento = int(entrada[1])
        
        if letra_fileira not in letras_fileiras:
            print("Fileira inválida.")
            continue
        
        if 0 < numero_assento <= len(sala_de_cinema[letras_fileiras.index(letra_fileira)]):
            numero_fileira = letras_fileiras.index(letra_fileira)
            if sala_de_cinema[numero_fileira][numero_assento - 1] == "disponível":
                sala_de_cinema[numero_fileira][numero_assento - 1] = "vendida"
                quantidade_ingressos -= 1
                recibo.append(f"{letra_fileira}{numero_assento}")
                print(f"{letra_fileira}{numero_assento} vendida com sucesso")
                if quantidade_ingressos == 0:
                    return recibo
            else:
                print(f"{letra_fileira}{numero_assento} já está vendida")
        else:
            print("Assento inválido.")

def mostrar_cadeiras(sala_de_cinema):
    letras_fileiras = string.ascii_uppercase[:len(sala_de_cinema)]
    for i, fileira in enumerate(sala_de_cinema):
        print(f"Fileira {letras_fileiras[i]}: ", end="")
        for j, status in enumerate(fileira):
            if status == "disponível":
                print(f"{letras_fileiras[i]}{j + 1} Disponível", end="  ")
            else:
                print(f"{letras_fileiras[i]}{j + 1} Vendida", end="  ")
        print()  # Quebra de linha para a próxima fileira

def exibir_recibo(nome, cpf, filme, horario, cadeiras, total):
    print("____________________________")
    print("\nRecibo de Compra")
    print("Nome: ", nome)
    print("CPF: ", cpf)
    print("Filme: ", filme)
    print("Horário: ", horario)
    print("Cadeiras: ", ", ".join(cadeiras))
    print("Total a pagar: R$", total)
    print("____________________________")
def acesso_admin(cursor, conn):
    while True:
        print("Menu de Administração:")
        print("1. Adicionar filme")
        print("2. Remover filme")
        print("3. Definir preço de ingresso")
        print("4. Adicionar sessão")
        print("5. Listar sessões")
        print("6. Adicionar sinopse")
        print("7. cadastrar novo adm")
        print("8. menu lanchonete")
        print("9. retornar ao menu principal")
        opcao_admin = input("Escolha uma opção: ")

        
        if opcao_admin == '1':
            titulo_filme = input("Digite o título do filme que deseja adicionar: ")
            adicionar_filme(cursor, titulo_filme)
            conn.commit()
            print(f"Filme '{titulo_filme}' adicionado com sucesso.")
        elif opcao_admin == '2':
            titulo_filme = input("Digite o título do filme que deseja remover: ")
            remover_filme(cursor, titulo_filme)
            conn.commit()
            print(f"Filme '{titulo_filme}' removido com sucesso.")
        elif opcao_admin == '3':
            catalogo_filmes = obter_catalogo(cursor)
            print("Filmes disponíveis:")
            for i, filme in enumerate(catalogo_filmes, 1):
                print(f"{i}. {filme[1]} - Preço atual: R${filme[2]:.2f}")
            escolha_filme = input("Escolha o filme que deseja definir o preço ou '0' para voltar: ")
            if escolha_filme == '0':
                continue
            if escolha_filme.isdigit() and 1 <= int(escolha_filme) <= len(catalogo_filmes):
                filme_escolhido = catalogo_filmes[int(escolha_filme) - 1]
                novo_preco = input(f"Digite o novo preço para '{filme_escolhido[1]}' (no formato 14.00): ")
                try:
                    novo_preco = float(novo_preco)
                    definir_preco(cursor, filme_escolhido[0], novo_preco)
                    conn.commit()
                    print(f"Preço definido com sucesso para '{filme_escolhido[1]}'")
                except ValueError:
                    print("Formato de preço inválido. Use o formato 14.00.")
            else:
                print("Opção inválida.")
        elif opcao_admin == '4':
            catalogo_filmes = obter_catalogo(cursor)
            print("Filmes disponíveis:")
            for i, filme in enumerate(catalogo_filmes, 1):
                print(f"{i}. {filme[1]}")
            escolha_filme = input("Escolha o filme para adicionar uma sessão (ou '0' para voltar): ")
            if escolha_filme == '0':
                continue
            if escolha_filme.isdigit() and 1 <= int(escolha_filme) <= len(catalogo_filmes):
                filme_escolhido = catalogo_filmes[int(escolha_filme) - 1]
                horario_sessao = input("Digite o horário da sessão (exemplo: 18:00): ")
                dublado = input("Digite 'dublado' para dublado ou 'legendado' para legendado: ").lower()
                if dublado not in ('dublado', 'legendado'):
                    print("Opção inválida. Escolha 'dublado' ou 'legendado'.")
                    continue
                adicionar_sessao(cursor, filme_escolhido[0], horario_sessao, dublado)
                conn.commit()
                print("Sessão adicionada com sucesso.")
        elif opcao_admin == '5':
            listar_sessoes(cursor)

        elif opcao_admin == '6':
                listar_sessoes(cursor) 
                id_sessao = input("Digite o número da sessão à qual deseja adicionar uma sinopse: ")
                sinopse = input("Digite a sinopse: ")
                cursor.execute("UPDATE sessoes SET sinopse = ? WHERE id = ?", (sinopse, id_sessao))
                cursor.connection.commit()
                print("Sinopse adicionada com sucesso.")
        elif opcao_admin == '7':
             novo_admin_nome = input("Digite o nome do novo administrador: ")
             novo_admin_senha = input("Digite a senha do novo administrador: ")
             cursor.execute('''INSERT INTO usuarios (nome, senha, admin) VALUES (?, ?, ?)''', (novo_admin_nome, novo_admin_senha, 1))
             conn.commit()
             print("Novo administrador cadastrado com sucesso.")
        elif opcao_admin == '8':
             print("1- cadastrar bebida")
             print("2- cadastrar comida")
             opcao_lanchonete=input("selecione uma das opções: ")
             if opcao_lanchonete =='1':
              bebida = input("Digite o nome da bebida: ")
              preco_bebida = float(input("Digite o preço(0.00): "))
              cursor.execute('''INSERT INTO bebidas (nome,preco) VALUES (?,?)''',(bebida,preco_bebida))
              conn.commit()
             elif opcao_lanchonete =='2':
              comida = input("Digite a senha do novo administrador: ")
              cursor.execute('''INSERT INTO bebidas (nome) VALUES (?)''', (comida))
              conn.commit()
             elif opcao_lanchonete =='3':
                 cursor.execute("SELECT nome,preco FROM bebidas")
                 bebidas=cursor.fetchall()
                 preco_bebida=cursor.fetchall()
                 print("lista de bebidas")
                 for bebida in bebidas:
                     print(f"{bebida[0]:<20 } {bebida[1]: .2f}")
             
        elif opcao_admin == '9':
             return  
        else:
         print("Opção inválida.")

def adicionar_sessao(cursor, filme_id, horario, dublado, sinopse=""):
    cursor.execute("INSERT INTO sessoes (filme_id, horario, dublado, sinopse) VALUES (?, ?, ?, ?)", (filme_id, horario, dublado, sinopse))
    cursor.execute("UPDATE filmes SET sinopse = ? WHERE id = ?", (sinopse, filme_id))
def listar_sessoes(cursor):
    cursor.execute("SELECT sessoes.id, filmes.titulo, sessoes.horario, sessoes.dublado, sessoes.sinopse FROM sessoes INNER JOIN filmes ON sessoes.filme_id = filmes.id")
    sessoes = cursor.fetchall()

    print("Lista de Sessões:")
    for sessao in sessoes:
        sessao_id, titulo_filme, horario, dublado, sinopse = sessao[0], sessao[1], sessao[2], sessao[3], sessao[4]

        dublado_str = "Dublado" if dublado == "dublado" else "Legendado"
        print()
        print("_______________________")
        print(f"Sessão ID: {sessao_id}")
        print(f"Filme: {titulo_filme}")
        print(f"Horário: {horario}")
        print(f"Formato: {dublado_str}")
        print(f"Sinopse: {sinopse}")
        print("_______________________")
        print()
if __name__== "__main__":
    main()