<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>BinDrop - Login</title>

    <link rel="icon" href="favicon.ico" type="image/x-icon" />
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


        input[type="user"], input[type="password"] { padding: 10px; border: 1px solid #ccc; border-radius: 5px; }

        button { padding: 10px; border: none; border-radius: 5px; background-color: #3498db; color: white; cursor: pointer; transition: background-color 0.2s ease; }
        button:hover { background-color: #2980b9; }
    </style>

    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script>
        async function autenticar(api) {
            const username = document.getElementById("email").value.trim();
            const password = document.getElementById("senha").value.trim();

            if (!username || !password) { Swal.fire("Campos obrigatórios", "Preencha todos os campos.", "warning"); return; }

            try {
                const resposta = await fetch("https://servidordomal.fun/api/" + api, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });

                if (resposta.status == 200 || resposta.status == 201) { window.location.href = "/"; } 
                else if (resposta.status == 401) { Swal.fire("Erro", "Usuário ou senha incorretos!"); }
                else if (resposta.status == 409) { Swal.fire("Erro", "Este nome de usuário já está em uso!"); }
            } catch (erro) { Swal.fire("Erro", "Erro na conexão com o servidor.", "error"); }
        }

        window.onload = () => {
            const form = document.querySelector("form");
            const botoes = form.querySelectorAll("button");

            botoes[0].addEventListener("click", function (event) { event.preventDefault(); autenticar("login"); });
            botoes[1].addEventListener("click", function (event) { event.preventDefault(); autenticar("signup"); });
        };
    </script>
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
