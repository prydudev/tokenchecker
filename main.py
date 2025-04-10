import os, asyncio, aiohttp, json, time, pyperclip; from rich.console import Console; from rich.theme import Theme; from rich.style import Style; from pathlib import Path

theme = Theme({'m': '#e3e3e3', 'info': Style(color="#8fcceb", bgcolor="#2a3139"), 'error': Style(color="#eb8f8f", bgcolor="#392a2a"), 'success': Style(color="#a4eb8f", bgcolor="#1e392a"), 'nitro': Style(color="#c38feb", bgcolor="#392a39"), 'locked': Style(color="#ebce8f", bgcolor="#393329")})
console = Console(theme=theme)

class TokenChecker:
    def __init__(self): 
        self.tokens = {k: set() for k in ['valid', 'invalid', 'checked', 'email', 'phone', 'nitro', 'locked']}
        [Path(p).mkdir(exist_ok=True) for p in ["output", "output/Verified"]]; self.load_config()
        self.valid_count = self.invalid_count = self.locked_count = 0; self.username_cache = {}
        self.headers = {'Accept': '*/*', 'Authorization': '', 'Host': 'discord.com', 'Referer': 'https://discord.com/channels/@me', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'X-Discord-Locale': 'en-US'}

    def load_config(self): 
        try: self.config = json.load(open("config.json", "r"))
        except: self.config = {"SHOW_INVALID": True, "AUTO_REMOVE_INVALID": False}; json.dump(self.config, open("config.json", "w"), indent=4)

    def menu(self, options): os.system('cls'); [console.print(f"[m]{opt}[/]") for opt in options]; return console.input("\n[m]❯ [/]").strip().lower()

    def settings(self):
        while True:
            choice = self.menu([
                f"[info]1[/] Show Invalid: [info]{('Yes' if self.config['SHOW_INVALID'] else 'No')}[/]", 
                f"[info]2[/] Auto Remove Invalid: [info]{('Yes' if self.config['AUTO_REMOVE_INVALID'] else 'No')}[/]",
                "[error]b[/] Back"
            ])
            if choice == "1": os.system('cls'); self.update_config("SHOW_INVALID", console.input("\n[m]Show invalid tokens? ([success]y[/]/[error]n[/]): ").lower())
            elif choice == "2": os.system('cls'); self.update_config("AUTO_REMOVE_INVALID", console.input("\n[m]Automatically remove invalid tokens? ([success]y[/]/[error]n[/]): ").lower())
            elif choice == "b": break
    
    def update_config(self, setting, yn):
        if yn in ['y', 'n']: self.config[setting] = (yn == 'y'); json.dump(self.config, open("config.json", "w"), indent=4)
        console.print("[success]✓ Setting updated![/]"); time.sleep(1); os.system('cls')
    
    async def get_token_username(self, token):
        if token in self.username_cache: return self.username_cache[token]
        if not token or len(token) < 50: return None
        
        headers = self.headers.copy(); headers['Authorization'] = token
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=aiohttp.ClientTimeout(total=5), ssl=False) as r:
                    if r.status == 200: data = await r.json(); self.username_cache[token] = data.get('username'); return self.username_cache[token]
        except: pass
        return None

    def token_manager(self):
        while True:
            choice = self.menu(["[success]1[/] Add", "[info]2[/] Manage", "[error]b[/] Back"])
            if choice == "1": self.add_token()
            elif choice == "2": self.manage_tokens()
            elif choice == "b": break
    
    async def add_token_async(self, token):
        if not token or len(token) < 50: console.print("[error]✗ Invalid token format[/]"); return False
        username = await self.get_token_username(token)
        if username: open("tokens.txt", "a", encoding="utf-8").write(f"\n{token}"); console.print(f"[success]✓ Token {token[:24]}.. with username {username} has been added![/]"); return True
        else: console.print("[error]✗ Could not verify token[/]"); return False
    
    def add_token(self):
        os.system('cls'); console.print("[success]Add Token[/]")
        token = console.input("\n[m]Enter token: [/]").strip()
        if token: asyncio.run(self.add_token_async(token))
        console.print("\n[m]Press [info]Enter[/][m] to continue...[/]"); input()
    
    def has_tokens(self, file_path): return len(self.read_tokens(file_path)) > 0
    
    def manage_tokens(self):
        while True:
            options = ["[success]1[/] Valid", "[error]2[/] Invalid"]
            has_locked = self.has_tokens("output/locked.txt"); has_nitro = self.has_tokens("output/nitro.txt")
            option_num = 3; locked_option = option_num if has_locked else 0
            if has_locked: options.append(f"[locked]{option_num}[/] Locked"); option_num += 1
            options.append(f"[info]{option_num}[/] Verified"); option_num += 1
            nitro_option = option_num if has_nitro else 0
            if has_nitro: options.append(f"[nitro]{option_num}[/] Nitro"); option_num += 1
            options.append("[error]b[/] Back")
            
            choice = self.menu(options)
            if choice == "1": self.manage_category("output/valid.txt", "Valid")
            elif choice == "2": self.manage_category("output/invalid.txt", "Invalid")
            elif choice == str(locked_option): self.manage_category("output/locked.txt", "Locked")
            elif choice == str(option_num-1 if has_nitro else option_num-2):
                sub_choice = self.menu(["[success]1[/] Email", "[success]2[/] Phone", "[error]b[/] Back"])
                if sub_choice == "1": self.manage_category("output/Verified/email.txt", "Email Verified")
                elif sub_choice == "2": self.manage_category("output/Verified/phone.txt", "Phone Verified")
            elif choice == str(nitro_option): self.manage_category("output/nitro.txt", "Nitro")
            elif choice == "b": break
    
    async def get_usernames(self, tokens): return {t: u for t, u in zip(tokens, await asyncio.gather(*[self.get_token_username(t) for t in tokens])) if u}
    
    def manage_category(self, file_path, category_name):
        tokens = self.read_tokens(file_path)
        if not tokens: console.print(f"[error]✗ No tokens found in {category_name} category[/]"); console.print("\n[m]Press [info]Enter[/][m] to continue...[/]"); input(); return
        
        console.print(f"[info]Loading tokens...[/]")
        token_usernames = asyncio.run(self.get_usernames(tokens))
        
        while True:
            os.system('cls')
            [console.print(f"[locked]{i}[/] {t[:24]}..{(' ' + token_usernames.get(t, '')) if token_usernames.get(t) else ''}") for i, t in enumerate(tokens, 1)]
            
            choice = console.input("\n[m]Enter token number to manage or [error]b[/][m] to go back: [/]").strip().lower()
            if choice == "b": break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(tokens): self.manage_token(tokens[idx], file_path, tokens); tokens = self.read_tokens(file_path)
                else: console.print("[error]✗ Invalid selection[/]"); time.sleep(1)
            except ValueError: console.print("[error]✗ Invalid input[/]"); time.sleep(1)
    
    def read_tokens(self, file_path):
        try: return [t.strip() for t in open(file_path, "r", encoding="utf-8").read().splitlines() if t.strip()]
        except: return []
    
    def get_token_count(self):
        try: return len(set(self.read_tokens("tokens.txt")))
        except: return 0
    
    def manage_token(self, token, file_path, all_tokens):
        while True:
            username = asyncio.run(self.get_token_username(token)) or ""
            choice = self.menu([f"[info]Selected Token:[/] {token[:24]}..{(' ' + username) if username else ''}", 
                              "[success]1[/] Copy to Clipboard", "[error]2[/] Remove Token", "[error]b[/] Back"])
            
            if choice == "1": pyperclip.copy(token); console.print("[success]✓ Token copied to clipboard![/]"); time.sleep(1)
            elif choice == "2": all_tokens.remove(token); open(file_path, "w", encoding="utf-8").write('\n'.join(all_tokens)); console.print("[success]✓ Token removed![/]"); time.sleep(1); break
            elif choice == "b": break

    def main_menu(self):
        while True:
            token_count = self.get_token_count()
            choice = self.menu([f"[success]1[/] Start ({token_count})", 
                              "[locked]2[/] Token Manager", 
                              "[info]3[/] Settings", 
                              "[error]b[/] Back"])
            if choice == "1": asyncio.run(self.main())
            elif choice == "2": self.token_manager()
            elif choice == "3": self.settings()
            elif choice == "b": break

    async def check_token(self, session, token):
        if not token or len(token) < 50:
            if self.config['SHOW_INVALID']: console.print(f"[error]✗ {token}[/]")
            self.tokens['invalid'].add(token); self.tokens['checked'].add(token); self.invalid_count += 1; return

        headers = self.headers.copy(); headers['Authorization'] = token

        while True:
            try:
                async with session.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=aiohttp.ClientTimeout(total=3), ssl=False) as r:
                    if r.status == 429: await asyncio.sleep(float(r.headers.get('Retry-After', 1))); continue
                    elif r.status == 401:
                        if self.config['SHOW_INVALID']: console.print(f"[error]✗ {token}[/]")
                        self.tokens['invalid'].add(token); self.invalid_count += 1; return
                    elif r.status == 403:
                        console.print(f"[locked]🔒 {token}[/]")
                        self.tokens['locked'].add(token); self.locked_count += 1; return
                    elif r.status == 200:
                        data = await r.json(); username = data.get('username'); padding = " " * (30 - len(username))
                        status = [f"[m]{username}{padding}[/]", f"[{'success' if (email_ver:=data.get('verified', False)) else 'error'}]{'✓' if email_ver else '✗'}[/]", f"[{'success' if (phone_ver:=bool(data.get('phone'))) else 'error'}]{'✓' if phone_ver else '✗'}[/]", f"[{'success' if (nitro:=data.get('premium_type', 0)) else 'error'}]{'✓' if nitro else '✗'}[/]"]
                        console.print(f"[success]✓[/] {token[:33]}.. │ " + " │ ".join(status))
                        self.tokens['valid'].add(token)
                        if email_ver: self.tokens['email'].add(token)
                        if phone_ver: self.tokens['phone'].add(token)
                        if nitro: self.tokens['nitro'].add(token)
                        self.username_cache[token] = username
                        self.valid_count += 1; return
            except: await asyncio.sleep(0.1); continue

    def remove_invalid_tokens(self):
        try:
            all_tokens = set(self.read_tokens("tokens.txt"))
            valid_tokens = all_tokens - self.tokens['invalid']
            open("tokens.txt", "w", encoding="utf-8").write('\n'.join(sorted(valid_tokens)))
            console.print(f"[success]✓ Removed {self.invalid_count} invalid tokens from tokens.txt[/]")
        except Exception as e: console.print(f"[error]✗ Error removing invalid tokens: {str(e)}[/]")

    async def main(self):
        os.system('cls')
        tokens = self.read_tokens("tokens.txt")
        if not tokens: console.print(f"[error]✗ tokens.txt not found or empty[/]"); console.print("\n[m]Press [info]Enter[/][m] to continue...[/]"); input(); return

        console.print(f"[success]✓ Loaded {len(tokens)} tokens[/]"); console.print()
        self.valid_count = self.invalid_count = self.locked_count = 0; start = time.time()
        
        connector = aiohttp.TCPConnector(limit=25, ssl=False, force_close=True)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=3)) as session:
            for i in range(0, len(tokens), 10):
                await asyncio.gather(*[self.check_token(session, token) for token in tokens[i:i+10]])
                if i + 10 < len(tokens): await asyncio.sleep(0.1)
        
        for f, t in {"output/valid.txt": self.tokens['valid'], "output/invalid.txt": self.tokens['invalid'], "output/locked.txt": self.tokens['locked'], "output/Verified/email.txt": self.tokens['email'], "output/Verified/phone.txt": self.tokens['phone'], "output/nitro.txt": {t for t in self.tokens['nitro'] if t in self.tokens['valid']}}.items():
            open(f, "w").write('\n'.join(sorted(t)))

        total = len(tokens)
        valid_percent = (self.valid_count / total) * 100 if total > 0 else 0
        invalid_percent = (self.invalid_count / total) * 100 if total > 0 else 0
        locked_percent = (self.locked_count / total) * 100 if total > 0 else 0

        console.print("\n" + "─" * 65, style="m")
        console.print(f"[info]Time: {int((time.time()-start)//60)}m {int((time.time()-start)%60)}s[/]")
        console.print(f"[success]✓ Valid: {self.valid_count} ({valid_percent:.2f}%)[/]")
        console.print(f"[error]✗ Invalid: {self.invalid_count} ({invalid_percent:.2f}%)[/]")
        if self.locked_count > 0: console.print(f"[locked]🔒 Locked: {self.locked_count} ({locked_percent:.2f}%)[/]")
        if len(self.tokens['nitro']) > 0: console.print(f"[nitro]Nitro: {len(self.tokens['nitro'])}[/]")
        console.print("─" * 65, style="m")
        
        if self.invalid_count > 0:
            if self.config['AUTO_REMOVE_INVALID']:
                console.print(f"\n[info]Found {self.invalid_count} invalid tokens. Auto-removing...[/]")
                self.remove_invalid_tokens()
            else:
                console.print(f"\n[error]Found {self.invalid_count} invalid tokens[/]")
                if console.input("[m]Remove invalid tokens from tokens.txt? ([success]y[/]/[error]n[/]): [/]").strip().lower() == 'y':
                    self.remove_invalid_tokens()
        
        console.print("\n[m]Press [info]Enter[/][m] to continue...[/]"); input()

if __name__ == "__main__": TokenChecker().main_menu()