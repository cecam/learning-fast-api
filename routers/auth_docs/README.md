# Documentación de Autenticación con FastAPI

## Descripción General

Esta documentación proporciona una visión general del sistema de autenticación implementado utilizando FastAPI. El código incluye autenticación de usuarios, generación de tokens JWT y funcionalidades de gestión de usuarios.

## Importaciones

```python
from fastapi import APIRouter, Depends, HTTPException, status
from models import AuthenticatedUser, UserDB, Token, TokenData
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
```

## Configuración

### Configuración del Token JWT

- **SECRET_KEY**: La clave secreta utilizada para firmar el token JWT.
- **ALGORITHM**: El algoritmo utilizado para firmar el token JWT.
- **ACCESS_TOKEN_EXP_MINUTES**: El tiempo de expiración del token de acceso en minutos.

```python
SECRET_KEY = "ea480dc9fd80680bde59fa4d340cb2b68ad8d9373e01ec5a0f3860e9ac561e54"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXP_MINUTES = 30
```

### Contexto de Criptografía de Contraseñas

- **crypt**: Contexto de hash de contraseñas utilizando bcrypt.

```python
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

### Base de Datos de Usuarios

Una base de datos en memoria de muestra con detalles de los usuarios.

```python
usersDB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "email@mail.com",
        "disabled": False,
        "hashed_password": "$2a$12$oJCK3EmBSF6EJhS8lfblHOu/DKtcgG9xGZzFPQ1lhV/4V9w3Q2E8"
    },
    "janedoe": {
        "username": "janedoe",
        "full_name": "Jane Doe",
        "email": "mail@mail.com",
        "disabled": True,
        "hashed_password": "$2a$12$oJCK3EmBSF6EJhS8lfblHOu/DKtcgG9xGZzFPQ1lhV/4V9w3Q2E8"
    }
}
```

## Enrutador de la API

```python
router = APIRouter(tags=["auth"])
```

## OAuth2 Password Bearer

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

## Funciones Utilitarias

### Buscar Usuario

Busca un usuario en la base de datos por nombre de usuario.

```python
def search_user(username: str):
    if username in usersDB:
        return UserDB(**usersDB[username])
    return None
```

### Verificar Contraseña

Verifica la contraseña en texto plano contra la contraseña hash.

```python
def verify_password(plain_password, hashed_password):
    return crypt.verify(plain_password, hashed_password)
```

### Obtener Hash de la Contraseña

Genera el hash de una contraseña en texto plano.

```python
def get_password_hash(password):
    return crypt.hash(password)
```

### Tiempo de Expiración del Token de Acceso

Devuelve el tiempo de expiración para el token de acceso.

```python
def access_token_expires():
    return datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXP_MINUTES)
```

## Dependencias de Autenticación

### Autenticar Usuario

Autentica al usuario utilizando el token JWT proporcionado.

```python
async def auth_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Token inválido")
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido")
    return search_user(token_data.username)
```

### Usuario Actual

Devuelve el usuario autenticado actual.

```python
async def current_user(token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado", headers={"WWW-Authenticate": "Bearer"})

    if user.disabled:
        raise HTTPException(status_code=400, detail="Usuario deshabilitado")

    return user
```

### Crear Token de Acceso

Crea un nuevo token de acceso.

```python
def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": access_token_expires()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## Endpoints de la API

### Inicio de Sesión

Autentica a un usuario y devuelve un token JWT.

```python
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = usersDB.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    user = search_user(form.username)

    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    access_token = {
        "username": user.username,
        "full_name": user.full_name,
        "exp": access_token_expires()
    }

    return {"access_token": create_access_token(access_token), "token_type": "bearer"}
```

### Leer Usuario Actual

Devuelve los detalles del usuario autenticado actual.

```python
@router.get("/users/me", response_model=AuthenticatedUser)
async def read_users_me(user: UserDB = Depends(current_user)):
    return user
```
