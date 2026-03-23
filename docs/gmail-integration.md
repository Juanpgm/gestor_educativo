# Gmail Integration

## Setup

### 1. Google Cloud Console

1. Create a project at https://console.cloud.google.com/
2. Enable the **Gmail API**
3. Create **OAuth 2.0 Client ID** credentials (Desktop application)
4. Download the JSON credentials file

### 2. Place Credentials

```bash
cp downloaded-credentials.json secrets/credentials/gmail_credentials.json
```

### 3. First-Time Authorization

Run the app locally. The first email send will open a browser for OAuth consent. After authorization, a token is saved at `secrets/credentials/gmail_token.json`.

### 4. Environment Variables

```
GMAIL_CREDENTIALS_PATH=secrets/credentials/gmail_credentials.json
GMAIL_TOKEN_PATH=secrets/credentials/gmail_token.json
```

## Usage

```json
POST /api/v1/email/enviar
Authorization: Bearer <token>
{
    "documento_id": 1,
    "destinatario": "parent@email.com",
    "asunto": "Diploma - Juan Pérez",
    "cuerpo_html": "<h1>Adjunto encontrará el diploma.</h1>"
}
```

The system:

1. Looks up the generated document by ID
2. Attaches the .docx file
3. Sends via Gmail API
4. Logs the operation

## Security Notes

- Gmail credentials stored in `secrets/` (gitignored)
- OAuth2 tokens auto-refresh when expired
- Only the `gmail.send` scope is requested (minimal permissions)
