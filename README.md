# Costume Quest 2 — Tradução PT-BR ⚠️ PROJETO ABANDONADO

> **⚠️ ATENÇÃO:** Este projeto foi **abandonado**. A tradução das strings foi concluída (4.286/4.287 — 99,9%), porém o jogo não inicializa corretamente com os arquivos modificados (tela preta). O problema técnico não foi resolvido. Os arquivos são disponibilizados para que outros desenvolvedores possam continuar o trabalho.

---

## 📋 Status

| | |
|---|---|
| **Jogo** | Costume Quest 2 |
| **Desenvolvedor** | Double Fine Productions |
| **Plataforma** | PC (Steam) |
| **Strings traduzidas** | **4.286 / 4.287 (99,9%)** |
| **Status do repack** | ❌ Jogo não inicializa (tela preta) |
| **Autor** | [crispinhatt](https://github.com/crispinhatt) |

---

## 🔧 O que foi feito

### Strings traduzidas
Todas as 4.286 strings do jogo foram traduzidas para PT-BR usando a API Claude Sonnet, com glossário consistente com o CQ1.

### Formato técnico descoberto

O CQ2 usa o **Double Fine Pack Format dfpf versão 5**, diferente do dfpf v2 usado no CQ1.

| Característica | dfpf v2 (CQ1) | dfpf v5 (CQ2) |
|---|---|---|
| Endianness records | Big-endian | Big-endian |
| Header `file_records_offset` | Byte 56 | Byte 56 |
| StringTable header | `[uint32][0x31]` + texto | Sem header — começa direto com `StringTable{` |
| Encoding | UTF-8 | UTF-8 |
| Alinhamento blocos | 512 bytes | Variável |

### Estrutura dos records v5 (16 bytes, big-endian)

```
Pos +0  (DWORD): uncomp_size = d >> 8
Pos +3  (DWORD): name_offset = d >> 11          [sobreposição com pos+0]
Pos +8  (DWORD): file_offset = d >> 3
Pos +11 (DWORD): file_size   = ((d<<5)&0xFFFF_FFFF) >> 9
Pos +14 (DWORD): type_idx    = (((d<<4)&0xFFFF_FFFF)>>24)>>1  [cruza fronteira do record]
Pos +15 (BYTE):  comp_type   = b & 0x0F
```

### StringTables do CQ2

O `RgB_Stuff.~p` contém múltiplos StringTables:

| Nome | Índice | Offset | Tamanho | Descrição |
|------|--------|--------|---------|-----------|
| `stringtable/cq2_enus` | 8623 | 56.473.600 | 99.521 | EN principal |
| `stringtable/cq2_eses` | 8624 | 56.573.952 | 107.716 | ES (espaço suficiente para PT-BR) |
| `stringtable/cq2_engb` | 8629 | 56.981.504 | — | UK English |
| `stringtable/cqpc_usenglish` | 8634 | 57.090.048 | 1.438 | Strings PC |

### O que foi tentado para o repack

1. **Append no final do .~p** — Jogo não iniciava (o campo `JUNK_DATA_OFFSET` no byte 48 do header limitava a leitura)
2. **Atualizar `JUNK_DATA_OFFSET`** — Jogo continuava com tela preta
3. **Substituição in-place no slot `cq2_eses`** — PT-BR (104.090 bytes) cabe no espaço do espanhol (108.544 bytes). Records `cq2_enus` e `cq2_eses` redirecionados para o mesmo bloco PT-BR. Arquivo .~p com **tamanho idêntico ao original**. Mesmo assim, tela preta.

### Hipóteses não investigadas

- O jogo pode verificar um **checksum/hash** do arquivo .~p
- Pode existir um arquivo de **configuração de língua** não identificado
- O `CMAP008TEXT` (mapeamento de caracteres da fonte) pode precisar de atualização para incluir caracteres PT-BR (ã, ç, é, ê, etc.)
- O jogo pode usar o campo `cq2_enus` de forma diferente dos outros slots de língua

---

## 📁 Arquivos disponíveis

```
├── backup/
│   └── CQ2_strings_ptbr.json    ← 4.286 strings traduzidas (EN + PT-BR)
├── tools/
│   └── dfpf_parser.py           ← Parser dfpf v2 e v5
└── README.md
```

> Os arquivos `.~h` e `.~p` modificados **não são incluídos** pois causam tela preta.  
> O arquivo `CQ2_strings_ptbr.json` contém todas as traduções prontas para quem quiser continuar.

---

## 💡 Para quem quiser continuar

O principal obstáculo é fazer o jogo aceitar o arquivo modificado. Sugestões:

1. Investigar se existe um **checksum** do .~p armazenado em outro arquivo da pasta
2. Verificar o `CMAP008TEXT` — o original do EN tem caracteres de controle (`\t`, `\r\n`, `\"`) que podem estar sendo interpretados incorretamente
3. Usar o **DoubleFine-Explorer** ([bgbennyboy/DoubleFine-Explorer](https://github.com/bgbennyboy/DoubleFine-Explorer)) para comparar o arquivo gerado com o original via GUI
4. Comparar com a versão do jogo no **GOG** — pode ter uma estrutura diferente

---

## ⚠️ Aviso Legal

Esta é uma tradução **não oficial** criada por fãs, sem qualquer vínculo com a Double Fine Productions ou THQ Nordic. Distribuída gratuitamente para fins educacionais e de preservação.
