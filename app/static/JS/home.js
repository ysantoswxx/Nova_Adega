document.addEventListener("DOMContentLoaded", function () {

    const botoesCategoria =
        document.querySelectorAll(".categoria-btn");

    const produtos =
        document.querySelectorAll(".produto-card");


    botoesCategoria.forEach(function (botao) {

        botao.addEventListener("click", function () {

            const categoriaSelecionada =
                this.dataset.categoria;


            // Remove o ativo de todos os botões
            botoesCategoria.forEach(function (btn) {
                btn.classList.remove("ativo");
            });


            // Ativa o botão clicado
            this.classList.add("ativo");


            // Filtra os produtos
            produtos.forEach(function (produto) {

                const categoriaProduto =
                    produto.dataset.categoria;


                if (
                    categoriaSelecionada === "todos" ||
                    categoriaProduto === categoriaSelecionada
                ) {

                    produto.style.display = "";

                } else {

                    produto.style.display = "none";

                }

            });

        });

    });

});