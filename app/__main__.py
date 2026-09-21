"""Liga as tres portas e fica ouvindo.

Rode com:  .venv/bin/python -m app
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from app.canal.telegram import Telegram
from app.config import Config
from app.conversa import Conversa
from app.destino.planilha import Planilha
from app.interpretador.gemini import Gemini

MANUAL = Path("manual/MANUAL.md")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("robo")


def faltando(config: Config) -> list[str]:
    """Tudo que falta, de uma vez so.

    Um erro por vez faria a pessoa rodar cinco vezes para descobrir cinco
    coisas -- e na vespera da aula isso e meia hora perdida.
    """
    exigidos = {
        "TELEGRAM_TOKEN": config.telegram_token,
        "GEMINI_API_KEY": config.gemini_api_key,
        "PLANILHA_URL": config.planilha_url,
        "PLANILHA_SEGREDO": config.planilha_segredo,
        "AUTORIZADOS": config.autorizados,
    }
    return [f"falta {nome} no .env" for nome, valor in exigidos.items()
            if not valor.strip()]


def main() -> int:
    config = Config()

    problemas = faltando(config)
    if problemas:
        print("O robo nao pode subir:")
        for p in problemas:
            print(f"  - {p}")
        print("\nO README explica onde conseguir cada um.")
        return 1

    if not MANUAL.exists():
        print(f"Falta {MANUAL}. E o manual da sua agencia -- sem ele o robo nao "
              "sabe a sua regra de negocio.")
        return 1

    manual = MANUAL.read_text(encoding="utf-8")
    canal = Telegram(config.telegram_token)
    conversa = Conversa(
        interpretador=Gemini(config.gemini_api_key, config.gemini_modelo, manual),
        destinos=[Planilha(config.planilha_url, config.planilha_segredo)],
        config=config)

    log.info("no ar. manda a venda no Telegram.")
    while True:
        try:
            for msg in canal.receber():
                resposta = conversa.receber(msg)
                if resposta:
                    canal.responder(msg.conversa, resposta)
        except KeyboardInterrupt:
            log.info("ate logo.")
            return 0
        except Exception as erro:
            # Nao derrubar por um piscar de rede. Numa aula ao vivo, um robo que
            # morre no primeiro timeout e o fim da demonstracao.
            log.warning("tropecei, continuo: %s", erro)
            time.sleep(3)


if __name__ == "__main__":
    sys.exit(main())
