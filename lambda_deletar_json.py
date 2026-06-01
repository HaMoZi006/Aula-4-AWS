import boto3
import json
import os

s3     = boto3.client('s3')
BUCKET = os.environ.get('BUCKET_NAME', 'SEU-BUCKET-AQUI')


def lambda_handler(event, context):
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body or '{}')

    key      = body.get('key', '').strip()
    thumb_key = body.get('thumbKey', '').strip()

    if not key:
        return resposta(400, {'error': 'Campo "key" é obrigatório'})

    # Deleta o MP3
    s3.delete_object(Bucket=BUCKET, Key=key)
    print(f"Deletado: {key}")

    # Deleta a capa junto, se existir
    if thumb_key:
        s3.delete_object(Bucket=BUCKET, Key=thumb_key)
        print(f"Capa deletada: {thumb_key}")

    # Atualiza o musicas.json removendo a entrada com aquela url
    try:
        obj     = s3.get_object(Bucket=BUCKET, Key='musicas.json')
        musicas = json.loads(obj['Body'].read().decode('utf-8'))
        musicas = [m for m in musicas if not m.get('url', '').endswith(key.split('/')[-1])]
        s3.put_object(
            Bucket=      BUCKET,
            Key=         'musicas.json',
            Body=        json.dumps(musicas, ensure_ascii=False, indent=2).encode('utf-8'),
            ContentType= 'application/json',
        )
        print(f"musicas.json atualizado — total: {len(musicas)} músicas")
    except Exception as e:
        print(f"Aviso: não foi possível atualizar musicas.json — {e}")

    return resposta(200, {'ok': True})


def resposta(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type':                 'application/json',
        },
        'body': json.dumps(body),
    }
