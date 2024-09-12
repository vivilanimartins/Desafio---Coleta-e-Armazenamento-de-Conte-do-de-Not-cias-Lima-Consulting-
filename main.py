from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import pandas as pd
from google.oauth2 import service_account

app = FastAPI()

# Modelo de dados para a API
class Article(BaseModel):
    title: str
    content: str

# Função para obter o conteúdo limpo de um URL
def get_clean_content(url):
    # Obtendo o conteúdo da resposta
    response = requests.get(url)
    content = response.text
    soup = BeautifulSoup(content, 'html.parser')

    # Encontrando todos os elementos que têm a div <div data-testid="edinburgh-card">
    elements = soup.find_all("div", {"data-testid": "edinburgh-card"})

    result = []
    for element in elements:
        # Obtendo o texto do <h2> presente na div
        h2_text = element.find("h2").get_text()

        # Encontrando a tag de parágrafo (<p>) presente na div
        p_tag = element.find("p")

        # Verificando se há uma tag de parágrafo encontrada
        if p_tag:
            p_text = p_tag.get_text()
        else:
            p_text = None

        # Encontrando o elemento <span> com o último update
        last_updated_element = element.find("span", {"data-testid": "card-metadata-lastupdated"})

        # Verificando se o elemento <span> com o último update foi encontrado
        if last_updated_element:
            last_updated_text = last_updated_element.get_text()
        else:
            last_updated_text = None

        # Encontrando o elemento <span> com o tópico da notícia
        topic_element = element.find("span", {"data-testid": "card-metadata-tag"})

        # Verificando se o elemento <span> com o tópico da notícia foi encontrado
        if topic_element:
            topic_text = topic_element.get_text()
        else:
            topic_text = None

        result.append({"title": h2_text, "description": p_text, "last_Update": last_updated_text, "topic": topic_text})

    return result

# Rota Raiz
@app.get("/")
def raiz():
    clean_content = get_clean_content('https://www.bbc.com/')
    return clean_content

# Conexão com o BigQuery
scopes=["https://www.googleapis.com/auth/cloud-platform"]

credentials = service_account.Credentials.from_service_account_info(
{
  "type": "service_account",
  "project_id": "voltaic-circuit-435323-i4",
  "private_key_id": "71f87250ab47fb4316008516bdf9c29be1562f3c",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQChNRkspxuORVui\nzzLLJZRlSl2uhVGyy+5NXiBJ+Nq6SfGZwUheLn8no9MRDvnZhQS7hRc5Pj6GAfx7\nkC5S2w9fZKj7aDTc+ZTVHswpBJsg/1uIUWtEHNsbf7xpZgEufl8j4LVmN+hiaLbT\ns1SIyF7EcsgjGLeoaVdSd1Nq+Lr/wNTDKi/b7Pw0BEfJr+IKclIvOuZhhOy2kAcw\nzjWZvHsLVcLbslheuz1jUm5nmDa5CozEu/mRInXzcPx4Fp2Dpuat5p+Yh20t8a9y\nMV2dgAv+Z2UcygfYKjo6lj2GSVcCyCond2Vjps/f/MAr6QChl45XiDB/HXLGpjPB\nX7nJxlfnAgMBAAECggEAIpiDGQ6ZvswKsON3eppLgPtXJHtu/4h9UTQ4iLdztVPm\nGgGdVrzyw96IDtqgavp9fALBa6L8hwTJGvljv5tMbsPq8d04rw2Oz7fmx4y5//hd\nO+GBPCJXMU0V8aaW7VPodgok09V+tRPU3JTZOOuLTux1H/cPfwBwYX3DNKtBcl4n\n+JjLLlIyIVvnXSL7Nj7l/qPz7jQ17R6is0VIDnTsyPpi3FidInr9McKnwksRoQ9/\nYTqeVdjHt/23tz1M6+AkEchA+zzSm+nC8t8a0h+gqR84PsFvE0MfX48ZHA1inlUH\nHj+qlpjbyvdrql/74dZHpvZySzoDtHl9HfPwiyYH8QKBgQDMqkp922WCec43oSVz\n9WfcR/ksWi+ge9pcLtqL3NuXV8No+WPbCW739wtCIUOw3MFzqpvGtI5JrezuYY1w\nx6v5eFTvDTJhmpNQ07Stw1T6+QjP1TIHooDV/BgmPHGh6WQj8zm7C5B9Ov2v2Szw\nk21dwsM+TBzTkC3cO0L9TxODNwKBgQDJpFmNO3Nq/fLiltsczDRBuh36GKimmsl5\nkrYk13sXV4WTixMdj/p8sDgcTbR+W+V9TulDqZ7f2u+fzcO31GWXKVA4y16x6wpM\nOUP8EX5jsHNtOhgEfhn6CHFRvbA7zE2eYCp3JYX+Q47UJs09ly0jf6mX15GjKauw\nCmJUw3WI0QKBgHfjURuEh2P04h2oIf5ZROu+pXGbqsaBhpn1QEQpreBroqY9YIcQ\ncZaDem7UeYiC6DdPO00cuzTh0yaYsnfcHxtVp7sYqeiO2bjBKteW0pLpioXkRxg9\n0uaGc8cCJTZJN0Xv1mOBFLSm97AosbCDS89epWw6vbAYhyS4+jbUOYPlAoGAAWi+\nn3gM5HCF5AN94IOk0djFINxPQWrPgaP+1d8ToyQfcNqF9azt6TUqDziTzFZEEk4c\n3zYuQA49onZDqeM4GohVYTA6py+nUMUNrpNIuNWg2OCRDmb7M34fnJygwKo62KJ/\naXm/p/k85EqpIIcP77GSs9bz05oU8xP/f+wlxCECgYBabMMGuEZ3hk2p3QPnMNfq\nwyGc8WA1OwDzLOlWBZWG+qGBBQsQ0XvzJVeWAS3KHJ0h19lXk0Kq24dy9PNOJj1m\ncyfkPgKGzmVZsjsnvDrlfXwrNqzE67nbo9nJyjvI6r/EAYEv/uNeXT4l4c0A+fjD\nI1WZckDN7yA38wDbE86WcA==\n-----END PRIVATE KEY-----\n",
  "client_email": "appoutside@voltaic-circuit-435323-i4.iam.gserviceaccount.com",
  "client_id": "102223355493042300474",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/appoutside%40voltaic-circuit-435323-i4.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
)

# Criando um DataFrame com os dados obtidos
data = get_clean_content('https://www.bbc.com/')
df = pd.DataFrame(data)

# Gravando o DataFrame no BigQuery
project_id = "voltaic-circuit-435323-i4"
table_id = "teste.noticias"
df.to_gbq(table_id, project_id=project_id, if_exists='replace')
