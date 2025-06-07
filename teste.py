import requests
import sqlite3
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def coletar_dados():
    url = "https://api.thedogapi.com/v1/breeds"
    response = requests.get(url)
    if response.status_code == 200:
        print("Dados coletados com sucesso.")
        return response.json()
    else:
        print("Erro na requisição:", response.status_code)
        return []

def armazenar_dados(dados):
    conn = sqlite3.connect('projeto_rpa.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS racas (
            id INTEGER PRIMARY KEY,
            name TEXT,
            origin TEXT,
            life_span TEXT
        )
    ''')

    for dog in dados:
        cursor.execute('''
            INSERT OR IGNORE INTO racas (id, name, origin, life_span)
            VALUES (?, ?, ?, ?)
        ''', (
            dog['id'],
            dog['name'],
            dog.get('origin', 'N/A'),
            dog['life_span']
        ))

    conn.commit()
    conn.close()
    print("Dados armazenados no banco de dados.")

def processar_dados():
    conn = sqlite3.connect('projeto_rpa.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_processados (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            expectativa_min INTEGER,
            expectativa_max INTEGER
        )
    ''')

    cursor.execute("SELECT id, name, life_span FROM racas")
    dados = cursor.fetchall()

    for id, nome, life_span in dados:
        numeros = re.findall(r'\d+', life_span)
        if len(numeros) >= 2:
            expectativa_min, expectativa_max = int(numeros[0]), int(numeros[1])
        elif len(numeros) == 1:
            expectativa_min = expectativa_max = int(numeros[0])
        else:
            expectativa_min = expectativa_max = None

        cursor.execute('''
            INSERT OR REPLACE INTO dados_processados (id, nome, expectativa_min, expectativa_max)
            VALUES (?, ?, ?, ?)
        ''', (id, nome, expectativa_min, expectativa_max))

    conn.commit()
    conn.close()
    print("Dados processados e armazenados.")


def main():
    dados = coletar_dados()
    if dados:
        armazenar_dados(dados)
        processar_dados()
        #enviar_email()

if __name__ == "__main__":
    main()
