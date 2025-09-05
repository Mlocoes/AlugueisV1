"""
Router para Alias - Sistema de Grupos de Proprietários
Acesso exclusivo para administradores
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json
from datetime import datetime

from config import get_db
from models_final import Alias, AliasCreate, AliasUpdate, AliasResponse, Proprietario
from routers.auth import verify_token, is_admin

router = APIRouter(
    prefix="/api/extras",
    tags=["extras"],
    responses={404: {"description": "Alias não encontrado"}},
)

def verify_admin_access(current_user = Depends(is_admin)):
    """Verificar se o usuário é administrador"""
    return current_user

@router.get("/relatorios", response_model=List[AliasResponse])
async def listar_aliases_para_relatorios(db: Session = Depends(get_db)):
    """
    Endpoint público para consultar aliases em relatórios
    Não requer autenticação para facilitar integração com relatórios
    """
    try:
        aliases = db.query(Alias).all()
        return [alias.to_dict() for alias in aliases]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar aliases para relatórios: {str(e)}"
        )

# Rutas específicas (deben ir ANTES de las rutas dinámicas)
@router.get("/proprietarios/disponiveis")
async def listar_proprietarios_disponiveis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin_access)
):
    """Listar proprietários disponíveis para seleção em alias"""
    try:
        proprietarios = db.query(Proprietario).all()
        data = [{"id": p.id, "nome": p.nome, "sobrenome": p.sobrenome} for p in proprietarios]
        return {"success": True, "data": data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar proprietários disponíveis: {str(e)}")

@router.get("/estatisticas")
async def obter_estatisticas_alias(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin_access)
):
    """Obter estatísticas dos alias"""
    try:
        total_alias = db.query(func.count(Alias.id)).scalar()
        
        return {
            "total_alias": total_alias,
            "endpoint": "alias",
            "status": "ok"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.get("/{alias_id}/proprietarios/relatorios")
async def obter_proprietarios_alias_para_relatorios(
    alias_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint público para obter proprietários de um alias em relatórios
    Não requer autenticação para facilitar integração com relatórios
    """
    try:
        alias = db.query(Alias).filter(Alias.id == alias_id).first()
        if not alias:
            raise HTTPException(status_code=404, detail="Alias não encontrado")
        
        if not alias.id_proprietarios:
            return []
        
        proprietario_ids = json.loads(alias.id_proprietarios)
        proprietarios = db.query(Proprietario).filter(Proprietario.id.in_(proprietario_ids)).all()
        
        return [{"id": p.id, "nome": p.nome, "sobrenome": p.sobrenome} for p in proprietarios]
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato inválido de proprietários no alias")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter proprietários do alias para relatórios: {str(e)}"
        )

# Rutas generales
@router.get("/", response_model=List[AliasResponse])
async def listar_extras(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin_access)
):
    """Listar todos os alias (apenas administradores)"""
    try:
        query = db.query(Alias)
        alias_list = query.offset(skip).limit(limit).all()
        return [alias_obj.to_dict() for alias_obj in alias_list]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar alias: {str(e)}")

@router.get("/{alias_id}", response_model=AliasResponse)
async def obter_extra(
    alias_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(is_admin)
):
    """Obter um alias específico por ID"""
    alias_obj = db.query(Alias).filter(Alias.id == alias_id).first()
    if not alias_obj:
        raise HTTPException(status_code=404, detail="Alias não encontrado")
    
    return alias_obj.to_dict()

@router.post("/", response_model=AliasResponse)
async def criar_extra(
    alias_data: AliasCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin_access)
):
    """Criar um novo alias"""
    try:
        # Verificar se já existe um alias com o mesmo nome
        existing_alias = db.query(Alias).filter(Alias.alias == alias_data.alias).first()
        if existing_alias:
            raise HTTPException(status_code=400, detail="Já existe um alias com este nome")
        
        # Verificar se os proprietários existem
        if alias_data.id_proprietarios:
            try:
                proprietario_ids = json.loads(alias_data.id_proprietarios)
                if isinstance(proprietario_ids, list):
                    for prop_id in proprietario_ids:
                        proprietario = db.query(Proprietario).filter(Proprietario.id == prop_id).first()
                        if not proprietario:
                            raise HTTPException(status_code=400, detail=f"Proprietário com ID {prop_id} não encontrado")
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="id_proprietarios deve ser um JSON array válido")
        
        # Criar o novo alias
        new_alias = Alias(
            alias=alias_data.alias,
            id_proprietarios=alias_data.id_proprietarios
        )
        
        db.add(new_alias)
        db.commit()
        db.refresh(new_alias)
        
        return new_alias.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar alias: {str(e)}")

@router.put("/{alias_id}", response_model=AliasResponse)
async def atualizar_extra(
    alias_id: int,
    alias_data: AliasUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin_access)
):
    """Atualizar um alias existente"""
    try:
        alias_obj = db.query(Alias).filter(Alias.id == alias_id).first()
        if not alias_obj:
            raise HTTPException(status_code=404, detail="Alias não encontrado")
        
        # Verificar se o novo nome já existe (se foi fornecido)
        if alias_data.alias and alias_data.alias != alias_obj.alias:
            existing_alias = db.query(Alias).filter(Alias.alias == alias_data.alias).first()
            if existing_alias:
                raise HTTPException(status_code=400, detail="Já existe um alias com este nome")
        
        # Verificar proprietários se fornecidos
        if alias_data.id_proprietarios:
            try:
                proprietario_ids = json.loads(alias_data.id_proprietarios)
                if isinstance(proprietario_ids, list):
                    for prop_id in proprietario_ids:
                        proprietario = db.query(Proprietario).filter(Proprietario.id == prop_id).first()
                        if not proprietario:
                            raise HTTPException(status_code=400, detail=f"Proprietário com ID {prop_id} não encontrado")
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="id_proprietarios deve ser um JSON array válido")
        
        # Atualizar campos
        if alias_data.alias:
            alias_obj.alias = alias_data.alias
        if alias_data.id_proprietarios is not None:
            alias_obj.id_proprietarios = alias_data.id_proprietarios
        
        db.commit()
        db.refresh(alias_obj)
        
        return alias_obj.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar alias: {str(e)}")

@router.delete("/{alias_id}")
async def deletar_extra(
    alias_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin_access)
):
    """Deletar um alias"""
    try:
        alias_obj = db.query(Alias).filter(Alias.id == alias_id).first()
        if not alias_obj:
            raise HTTPException(status_code=404, detail="Alias não encontrado")
        
        db.delete(alias_obj)
        db.commit()
        
        return {"message": f"Alias '{alias_obj.alias}' deletado com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar alias: {str(e)}")

@router.get("/{alias_id}/proprietarios")
async def obter_proprietarios_do_alias(
    alias_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(is_admin)
):
    """Obter a lista detalhada de proprietários de um alias"""
    try:
        alias_obj = db.query(Alias).filter(Alias.id == alias_id).first()
        if not alias_obj:
            raise HTTPException(status_code=404, detail="Alias não encontrado")
        
        if not alias_obj.id_proprietarios:
            return {
                "alias": alias_obj.alias,
                "proprietarios": []
            }
        
        try:
            proprietario_ids = json.loads(alias_obj.id_proprietarios)
            proprietarios = []
            
            for prop_id in proprietario_ids:
                proprietario = db.query(Proprietario).filter(Proprietario.id == prop_id).first()
                if proprietario:
                    proprietarios.append({
                        "id": proprietario.id,
                        "nome": proprietario.nome,
                        "sobrenome": proprietario.sobrenome
                    })
            
            return {
                "alias": alias_obj.alias,
                "proprietarios": proprietarios
            }
        
        except json.JSONDecodeError:
            return {
                "alias": alias_obj.alias,
                "proprietarios": [],
                "erro": "Dados de proprietários inválidos"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter proprietários do alias: {str(e)}")
