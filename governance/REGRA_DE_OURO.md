# REGRA DE OURO — AUTOMAÇÃO DM R00-05

## 1. Simbologia

Nunca sair do padrão de simbologia AUTOMAÇÃO DM R00-05 aprovado para o projeto.

Famílias permitidas:
- Instrumento discreto: círculo.
- Display compartilhado: círculo inscrito em quadrado.
- Função executada em computador: hexágono.
- Função executada em PLC: losango inscrito em quadrado.

## 2. Dimensão nominal

Todos os símbolos funcionais devem possuir dimensão externa nominal de 12 mm.

- círculo: Ø 12 mm;
- círculo em quadrado: quadrado externo 12 x 12 mm;
- hexágono: envoltória externa nominal de 12 mm;
- losango em quadrado: quadrado externo 12 x 12 mm.

É proibido achatar, alongar, comprimir ou ampliar símbolos para acomodar texto ou layout.

O texto se adapta ao símbolo. O símbolo nunca se adapta ao texto.

## 3. Localização

A localização deve ser representada conforme o padrão do projeto:
- campo: sem linha horizontal;
- painel principal: uma linha contínua;
- atrás do painel: uma linha tracejada;
- painel local/equipamento: duas linhas contínuas.

## 4. Classificação antes do desenho

A ordem obrigatória é:

FUNÇÃO -> PLATAFORMA DE EXECUÇÃO -> LOCALIZAÇÃO -> SÍMBOLO AUTOMAÇÃO DM -> 12 mm -> LAYOUT.

Nunca escolher geometria por estética ou por espaço disponível.

## 5. Lógica funcional

- CMD != RUN.
- RUN != FAULT.
- AVAILABLE é estado independente.
- MAN/AUTO != LOCAL/REMOTO.
- Alarme não implica trip.
- Intertravamento exige causa, condição, efeito, equipamento afetado, feedback, reset, estado seguro e evidência.
- Sinal sem origem, destino, tipo, direção e função é órfão e bloqueante.

## 6. Informação documental

Nenhuma função, temporização, estado seguro, fail position, intertravamento, setpoint, sequência ou comunicação pode ser inventada.

Status aceitos:
- CONFIRMADO
- CONFIRMADO_COM_RESSALVA
- PROPOSTO
- CONFLITANTE
- TBD
- NÃO_APLICÁVEL

## 7. Regra de emissão

Qualquer violação deste documento é NÃO CONFORMIDADE CRÍTICA e bloqueia a aprovação da representação até correção ou justificativa técnica aprovada e rastreável.