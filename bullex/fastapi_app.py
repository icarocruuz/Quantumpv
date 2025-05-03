from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
import importlib
import inspect
import os
import sys
from typing import Any, Dict, Callable, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dynamic-api-router")

# Diretório base onde estão os arquivos Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adicionar diretórios ao path para resolver importações
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, '..'))

# Se você tiver um diretório 'bullex' no mesmo nível, adicione-o também
parent_dir = os.path.dirname(BASE_DIR)
if os.path.exists(os.path.join(parent_dir, 'bullex')):
    sys.path.append(os.path.join(parent_dir, 'bullex'))

# Criar a aplicação FastAPI
app = FastAPI(
    title="API Dinâmica",
    description="API que redireciona chamadas dinamicamente para funções em stable_api",
    version="1.0.0"
)

# Dicionário para armazenar em cache as funções encontradas
api_function_cache: Dict[str, Dict[str, Any]] = {}

# Armazenar instâncias de classes para reutilização
class_instances: Dict[str, Any] = {}

def load_module(module_name: str) -> Optional[Any]:
    """Carrega um módulo Python pelo nome"""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        logger.error(f"Erro ao importar o módulo {module_name}: {e}")
        return None

def find_function_in_module(module, function_path):
    """Encontra uma função/método em um módulo pelo caminho"""
    parts = function_path.split('.')
    current = module
    
    for part in parts:
        if hasattr(current, part):
            current = getattr(current, part)
        else:
            return None
    
    if callable(current):
        return current
    return None

def get_or_create_class_instance(module, class_name):
    """Obtém uma instância de classe existente ou cria uma nova"""
    cache_key = f"{module.__name__}.{class_name}"
    
    if cache_key in class_instances:
        return class_instances[cache_key]
    
    try:
        class_obj = getattr(module, class_name)
        instance = class_obj()
        class_instances[cache_key] = instance
        logger.info(f"Criada nova instância de {class_name}")
        return instance
    except Exception as e:
        logger.error(f"Erro ao criar instância de {class_name}: {e}")
        return None

def find_function_by_path(path: str):
    """Localiza uma função pelo caminho da URL"""
    # Remover a barra inicial
    if path.startswith('/'):
        path = path[1:]
    
    # Substituir traços por underscores
    path = path.replace('-', '_')
    
    # Verificar no cache
    if path in api_function_cache:
        logger.info(f"Função {path} encontrada no cache")
        return api_function_cache[path]
    
    # Carregar o módulo stable_api usando importação direta
    try:
        logger.info("Tentando importar stable_api diretamente")
        stable_api = importlib.import_module("stable_api")
        
        # Tentar encontrar a função diretamente
        if hasattr(stable_api, path):
            func = getattr(stable_api, path)
            if callable(func):
                logger.info(f"Função {path} encontrada diretamente no módulo stable_api")
                api_function_cache[path] = {'callable': func, 'instance': None}
                return api_function_cache[path]

        # Procurar em classes do módulo
        for class_name, class_obj in inspect.getmembers(stable_api, inspect.isclass):
            instance = get_or_create_class_instance(stable_api, class_name)
            if instance:
                for method_name, method_obj in inspect.getmembers(instance, inspect.ismethod):
                    if method_name == path:
                        logger.info(f"Método {path} encontrado na classe {class_name}")
                        api_function_cache[path] = {'callable': method_obj, 'instance': instance}
                        return api_function_cache[path]
    except ImportError as e:
        logger.warning(f"Não foi possível importar stable_api diretamente: {e}")
    
    # Se não conseguiu importar, tentar carregar o arquivo diretamente
    try:
        logger.info("Tentando carregar stable_api.py diretamente")
        spec = importlib.util.spec_from_file_location("custom_stable_api", os.path.join(BASE_DIR, "stable_api.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, path):
            func = getattr(module, path)
            if callable(func):
                logger.info(f"Função {path} encontrada diretamente no arquivo stable_api.py")
                api_function_cache[path] = {'callable': func, 'instance': None}
                return api_function_cache[path]
        
        # Procurar em classes do módulo
        for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
            try:
                instance = class_obj()
                for method_name, method_obj in inspect.getmembers(instance, inspect.ismethod):
                    if method_name == path:
                        logger.info(f"Método {path} encontrado na classe {class_name}")
                        api_function_cache[path] = {'callable': method_obj, 'instance': instance}
                        return api_function_cache[path]
            except Exception as e:
                logger.error(f"Erro ao instanciar {class_name}: {e}")
    except Exception as e:
        logger.warning(f"Não foi possível carregar stable_api.py diretamente: {e}")
    
    # Se ainda não encontrou, procurar nos subdiretórios
    for subdir in ['http', 'ws']:
        try:
            module_path = f"{subdir}.{path}" if '/' not in path else path.replace('/', '.')
            parts = module_path.split('.')
            
            if len(parts) >= 2:
                module_name = '.'.join(parts[:-1])
                func_name = parts[-1]
                
                module = load_module(module_name)
                if module and hasattr(module, func_name):
                    func = getattr(module, func_name)
                    if callable(func):
                        logger.info(f"Função {func_name} encontrada no módulo {module_name}")
                        api_function_cache[path] = {'callable': func, 'instance': None}
                        return api_function_cache[path]
        except Exception as e:
            logger.error(f"Erro ao procurar em {subdir}: {e}")
    
    return None

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def dynamic_api_router(request: Request, path: str):
    """Roteador dinâmico que processa qualquer rota e método"""
    logger.info(f"Recebida solicitação {request.method} para {path}")
    
    # Procurar a função pelo caminho
    func_info = find_function_by_path(path)
    
    if not func_info:
        logger.error(f"Nenhuma função encontrada para o caminho {path}")
        raise HTTPException(status_code=404, detail=f"Endpoint não encontrado: {path}")
    
    # Extrair parâmetros da solicitação
    params = {}
    
    # Para GET/DELETE, extrair dos query params
    if request.method in ["GET", "DELETE"]:
        for key, value in request.query_params.items():
            params[key] = value
    
    # Para POST/PUT/PATCH, extrair do corpo da solicitação
    elif request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
            if isinstance(body, dict):
                params.update(body)
            else:
                params["data"] = body
        except Exception as e:
            logger.warning(f"Erro ao processar corpo como JSON: {e}")
            # Se não for JSON, tentar form data
            try:
                form_data = await request.form()
                for key, value in form_data.items():
                    params[key] = value
            except Exception as e2:
                logger.warning(f"Erro ao processar corpo como form data: {e2}")
                # Se tudo falhar, tentar como texto
                try:
                    text = await request.body()
                    params["data"] = text
                except Exception as e3:
                    logger.error(f"Erro ao ler corpo da solicitação: {e3}")
    
    # Chamar a função com os parâmetros extraídos
    try:
        logger.info(f"Chamando {path} com parâmetros: {params}")
        
        # Verificar assinatura da função para passar apenas parâmetros válidos
        sig = inspect.signature(func_info['callable'])
        valid_params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            if param_name in params:
                valid_params[param_name] = params[param_name]
            elif param.default == inspect.Parameter.empty:
                logger.warning(f"Parâmetro obrigatório {param_name} não fornecido")
        
        result = func_info['callable'](**valid_params)
        
        # Tentar serializar o resultado para JSON
        try:
            return {"status": "success", "data": result}
        except Exception as e:
            # Se não for serializável, converter para string
            logger.warning(f"Resultado não serializável: {e}")
            return {"status": "success", "data": str(result)}
            
    except Exception as e:
        logger.error(f"Erro ao chamar {path}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """Endpoint inicial com instruções"""
    return {
        "message": "API dinâmica para stable_api",
        "usage": "Faça solicitações para /{nome_da_função} com os parâmetros apropriados"
    }

if __name__ == "__main__":
    import uvicorn
    import traceback
    
    # Tentar importar bullex para garantir que está disponível
    try:
        import bullex
        logger.info("Módulo bullex carregado com sucesso")
    except ImportError as e:
        logger.warning(f"Não foi possível importar o módulo bullex: {e}")
        logger.warning("Isto pode causar problemas se stable_api depender dele")
        
        # Criar um módulo bullex fake para resolver dependências
        try:
            import sys
            import types
            
            bullex_module = types.ModuleType("bullex")
            sys.modules["bullex"] = bullex_module
            logger.info("Criado módulo bullex mock para resolver dependências")
        except Exception as e2:
            logger.error(f"Erro ao criar módulo bullex mock: {e2}")
    
    # Iniciar o servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)