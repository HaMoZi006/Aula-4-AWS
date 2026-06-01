import boto3
import json
import os

s3     = boto3.client('s3')
BUCKET = os.environ.get('BUCKET_NAME', 'SEU-BUCKET-AQUI')
KEY    = 'musicas.json'


def lambda_handler(event, context):
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body or '{}')

    nome  = body.get('nome', '').strip()
    url   = body.get('url', '').strip()
    thumb = body.get('thumb', None)

    if not nome or not url:
        return resposta(400, {'error': 'Campos "nome" e "url" são obrigatórios'})

    # ── Lê o musicas.json atual do S3 ────────────────────────────────────────
    # Se o arquivo não existir ainda, começa com lista vazia
    try:
        obj     = s3.get_object(Bucket=BUCKET, Key=KEY)
        musicas = json.loads(obj['Body'].read().decode('utf-8'))
    except s3.exceptions.NoSuchKey:
        musicas = []

    # ── Adiciona a nova música ────────────────────────────────────────────────
    nova = {'nome': nome, 'url': url}
    if thumb:
        nova['thumb'] = thumb

    musicas.append(nova)
    print(f"Adicionando '{nome}' — total: {len(musicas)} músicas")  # CloudWatch

    # ── Salva o JSON atualizado de volta no S3 ────────────────────────────────
    s3.put_object(
        Bucket=      BUCKET,
        Key=         KEY,
        Body=        json.dumps(musicas, ensure_ascii=False, indent=2).encode('utf-8'),
        ContentType= 'application/json',
    )

    return resposta(200, {'ok': True, 'total': len(musicas)})


def resposta(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type':                 'application/json',
            'Access-Control-Allow-Origin':  '*',
            'Access-Control-Allow-Headers': 'content-type',
        },
        'body': json.dumps(body),
    }