import sys
import re
import os
import urllib.request
import urllib.parse
from datetime import datetime
import argparse
import json
from html import unescape

try:
    from googlesearch import search
except ImportError:
    print("[!] Módulo \"google\" não encontrado")
    print("    Por favor, instale-o usando:")
    print("\n    python3 -m pip install google")
    exit()

GROUP_NAME_REGEX = re.compile(r'(og:title\" content=\")(.*?)(\")')
GROUP_IMAGE_REGEX = re.compile(r'(og:image\" content=\")(.*?)(\")')

SAVE = "scrapped_%s.txt" % datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
tags_for_telegram = ["Cassino", "Roleta", "Multiplicador", "Renda extra", "Tigrinho", "Tiger", "Apostas", "Pitaco", "Dinheiro", "BR", "Ganhar Dinheiro", "Subway Surf"]

def pad(url):
    return urllib.parse.quote(url, safe='')

def linkcheck(url):
    print("\nTentando URL:", url, end='\r')
    group_info = {"name": None, "url": url, "image": None}
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(url, headers=hdr)
        resp = urllib.request.urlopen(req)
    except Exception:
        return group_info
    if (resp.getcode() != 404):
        resp = resp.read().decode("utf-8")
        group_info["name"] = unescape(GROUP_NAME_REGEX.search(resp).group(2))
        group_info["image"] = unescape(GROUP_IMAGE_REGEX.search(resp).group(2))
    return group_info

def scrape_group(txt, download_image=False, save_to_file=False):
    if isinstance(txt, bytes):
        txt = txt.decode("utf-8")
    match = []
    match2 = re.findall(r"(https:\/\/t\.me\/[a-zA-Z0-9_]+)", txt)
    match = [item for item in match2 if 'invite' in item]
    match = list(set(match))
    for lmt in match:
        lmt = pad(lmt)
        info = linkcheck(lmt)
        if info['name']:
            print("[i] Nome do Grupo:  ", info['name'])
            print("[i] Link do Grupo:  ", info['url'])
            print("[i] Imagem do Grupo: ", info['image'])
            lock.acquire()
            if SAVE.endswith(".json"):
                with open(SAVE, "r+", encoding='utf-8') as jsonFile:
                    data = json.load(jsonFile)
                    data.append(info)
                    jsonFile.seek(0)
                    json.dump(data, jsonFile)
                    jsonFile.truncate()
            else:
                with open(SAVE, "a", encoding='utf-8') as f:
                    write_data = " | ".join(info.values()) + "\n"
                    f.write(write_data)
            if download_image:
                image_path = urllib.parse.urlparse(info['image'])
                path, _ = urllib.request.urlretrieve(
                    info["image"], os.path.basename(image_path.path))
                print("[i] Caminho da Imagem: ", path)
            lock.release()

            if save_to_file:
                with open("results.txt", "a", encoding='utf-8') as file:
                    file.write(f"Nome do Grupo: {info['name']}\n")
                    file.write(f"Link do Grupo: {info['url']}\n")
                    file.write(f"Imagem do Grupo: {info['image']}\n\n")

def scrape_from_google():
    print("[*] Inicializando Scraping no Google...")
    resultados_encontrados = False
    for index in range(len(tags_for_telegram)):
        query = f"intext:https\\://t\\.me/ inurl:{tags_for_telegram[index]}"
        print("[*] Consultando o Google por Dorks ...")
        try:
            for url in search(query, tld="com", num=10, stop=None, pause=2):
                hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
                req = urllib.request.Request(url, headers=hdr)
                try:
                    txt = urllib.request.urlopen(req, timeout=10).read().decode("utf8")
                    scrape_group(txt, save_to_file=True)
                    resultados_encontrados = True
                except urllib.error.HTTPError as e:
                    print(f"[!] Erro HTTP ao acessar {url}: {e}")
                except urllib.error.URLError as e:
                    print(f"[!] Erro de URL ao acessar {url}: {e}")
                except Exception as e:
                    print(f"[!] Erro desconhecido ao acessar {url}: {e}")
        except Exception as e:
            print(f"[!] Erro desconhecido ao consultar o Google: {e}")
    
    if not resultados_encontrados:
        with open("results.txt", "w", encoding='utf-8') as file:
            file.write("Nenhum resultado obtido para a pesquisa.\n")

def main():
    global SAVE
    print("INICIANDO WhatScraper!!!")
    parser = argparse.ArgumentParser(description="Raspe Links de Grupos do Telegram")
    parser.add_argument("-j", "--json", action="store_true", help="Retorna um arquivo JSON em vez de um texto")
    parser.add_argument("-l", "--link", action="store", help="Mostra informações do grupo a partir do link do grupo")
    args = parser.parse_args()
    
    if args.link:
        scrape_group(args.link, download_image=True, save_to_file=True)
        return
    
    if args.json:
        SAVE = SAVE.split(".")[0]+".json"
        with open(SAVE, "w", encoding='utf-8') as jsonFile:
            json.dump([], jsonFile)
    
    print("""
    1> Raspar Grupos do Telegram no Google
    2> Raspar Grupos do Telegram de Sites de Compartilhamento de Grupos [MELHOR]
    """)

    try:
        inp = int(input("[#] Digite a Escolha: "))
    except Exception:
        print("\t[!] Escolha Inválida..")
        exit()

    if inp == 1:
        scrape_from_google()
    else:
        print("[!] Escolha Inválida..")

    print("[i] Resultados salvos em 'results.txt'")

if __name__ == "__main__":
    main()
