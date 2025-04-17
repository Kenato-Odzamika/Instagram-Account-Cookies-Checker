import json
import instaloader
import glob
import os
import time
import requests
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

console.print(r"""
[bold magenta]
    ____ _           _            
   / ___| |__   __ _| |_ ___ _ __ 
  | |   | '_ \ / _` | __/ __| '__|
  | |___| | | | (_| | || (__| |   
   \____|_| |_|____| \___|_||_|  
[/bold magenta]
""")

cookies_dir = "Cookies"
if not os.path.exists(cookies_dir):
    os.makedirs(cookies_dir)
    console.print(f"[bold yellow]⚠️ Папка {cookies_dir} не существовала, создана пустая папка[/bold yellow]")

json_files = glob.glob(os.path.join(cookies_dir, "*.json"))

if not json_files:
    console.print(f"[bold red]❌ Не найдено ни одного JSON-файла в папке {cookies_dir}[/bold red]")
    exit(1)

for json_file in json_files:
    console.print(f"\n[bold cyan]📂 Обработка файла: {os.path.basename(json_file)}[/bold cyan]")
    
    try:
        with open(json_file, 'r') as f:
            cookies_data = json.load(f)
    except json.JSONDecodeError:
        console.print(f"[bold red]❌ Ошибка: Файл {os.path.basename(json_file)} содержит некорректный JSON[/bold red]")
        continue
    except Exception as e:
        console.print(f"[bold red]❌ Ошибка при чтении файла {os.path.basename(json_file)}: {e}[/bold red]")
        continue

    if not cookies_data:
        console.print(f"[bold yellow]⚠️ Файл {os.path.basename(json_file)} пустой[/bold yellow]")
        continue
    
    if not all(isinstance(item, list) for item in cookies_data):
        cookies_data = [cookies_data]

    for cookies in cookies_data:
        session = requests.Session()
        
        try:
            for cookie in cookies:
                session.cookies.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie['domain'],
                    path=cookie['path'],
                    secure=cookie['secure'],
                    expires=int(cookie['expirationDate']) if 'expirationDate' in cookie else None
                )
        except (TypeError, KeyError) as e:
            console.print(f"[bold red]❌ Ошибка в структуре куки в файле {os.path.basename(json_file)}: {e}[/bold red]")
            continue

        L = instaloader.Instaloader()
        L.context._session = session
        
        try:
            username = L.context.test_login()
            if username:
                profile = instaloader.Profile.from_username(L.context, username)
                
                table = Table(title=f"📸 Информация об аккаунте {username} (файл: {os.path.basename(json_file)})", box=box.ROUNDED)
                table.add_column("Параметр", style="cyan", no_wrap=True)
                table.add_column("Значение", style="magenta")
                
                table.add_row("👤 Имя пользователя", username)
                table.add_row("📜 Полное имя", profile.full_name or "Не указано")
                table.add_row("📊 Подписчики", str(profile.followers))
                table.add_row("➡️ Подписки", str(profile.followees))
                table.add_row("🖼️ Публикации", str(profile.mediacount))
                table.add_row("📝 Биография", profile.biography or "Не указано")
                
                console.print(table)
                console.print(f"[bold green]✅ Аккаунт работает: {username}[/bold green]")
            else:
                console.print(f"[bold yellow]⚠️ Аккаунт не работает (из файла {os.path.basename(json_file)})[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ Ошибка при проверке аккаунта в файле {os.path.basename(json_file)}: {e}[/bold red]")
        
        time.sleep(1)