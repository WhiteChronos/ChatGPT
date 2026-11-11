# Ciclo de correção comprovado: recursos de coordenação

## Defeito observado

O verificador do pacote validava onze skills upstream, mas aceitava a ausência
da skill adicional de coordenação ou de sua referência evolution.md. Esse PASS
não garantia um pacote de doze skills utilizável.

## Reprodução e causa

O teste usa uma cópia temporária do pacote e remove um recurso de cada vez.
Antes da correção, ambas as condições deixaram de emitir ValueError: seis
testes executados, duas falhas no novo teste, código de saída 1.
Nenhuma skill instalada foi removida ou corrompida para realizar a prova.

## Correção e verificação

verify_package agora exige os dois recursos de coordenação usando a validação
de contenção de caminho já existente. Depois da correção: seis testes, zero
falhas, código de saída 0. As origens e os hashes upstream foram preservados.
Versão do adaptador: 1.1.1.

## Aprendizado

Recursos de integração mantidos pelo usuário precisam de verificação de
presença mesmo quando ficam fora dos hashes imutáveis do upstream. O teste
de regressão deve acompanhar alterações no conjunto obrigatório de recursos.

Esta prova demonstra um ciclo conduzido pelo agente neste escopo. Não é uma
garantia de correção autônoma de todos os defeitos ou disponibilidade contínua.
Os logs completos e seus hashes ficam nas evidências locais, fora do PR.
