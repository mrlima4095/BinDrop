<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>BinDrop - Login</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }
        body { background-color: #f0f2f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; flex-direction: column; overflow-x: hidden; }

        #container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 90%;
            text-align: center;
            position: relative;
        }

        #container h2, #container h3 { margin-bottom: 10px; color: #333; }
        #container p { margin-bottom: 20px; font-size: 0.9em; color: #666; }
        #container > button { display: block; width: 100%; margin-top: 10px; }
        #container h2 + button { margin-top: 10px; }

        #acoes { display: flex; align-items: center; gap: 5px; flex-wrap: nowrap; }
        #acoes img { width: 32px; height: 32px; object-fit: cover; cursor: pointer; }
        #acoes button { flex: 1; white-space: nowrap; }
    </style>
    <link rel="icon" href="favicon.ico" type="image/x-icon" />

    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script src="scripts/login.js" defer></script>
</head>
<body>
    <div id="container">
        <header>
            <h2>BinDrop - Login</h2>
            <p>Seja bem-vindo(a)!</p>
        </header>
        <form>
            <label for="email">ID:</label><br />
            <input type="user" id="email" name="email" required /><br /><br />

            <label for="senha">Senha:</label><br />
            <input type="password" id="senha" name="senha" required /><br /><br />

            <div id="acoes">
                <button type="button">Entrar</button>
                <button type="button">Registrar-se</button>
            </div>
            <br><a href="privacy">Política de Privacidade</a>
        </form>
    </div>
</body>
</html>
