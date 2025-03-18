# Mule Parent & BOM Repository  
[![MuleSoft 4.4+](https://img.shields.io/badge/MuleSoft-4.4%2B-blue.svg?logo=mulesoft)](https://docs.mulesoft.com/mule-runtime/4.4)
[![Java 8](https://img.shields.io/badge/Java-8-orange?logo=java)](https://adoptium.net/)
[![Maven 3.x](https://img.shields.io/badge/Maven-3.x-C71A36?logo=apache-maven)](https://maven.apache.org/)
[![Dependency Management](https://img.shields.io/badge/BOM-Dependency%20Management-success?logo=apachemaven)](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)

Bem-vindo(a) ao repositório **mule-parent-bom**!  
Aqui centralizamos dois artefatos fundamentais para padronizar projetos Mule 4:

1. **parent-pom.xml** – um **POM** “pai” que gerencia configurações de build, plugins e repositórios Maven.  
2. **bom.xml** (Bill of Materials) – define as **versões** das principais dependências e conectores Mule, facilitando o uso consistente em múltiplos projetos.

---

## 🚀 Sumário
1. [Descrição Geral](#descrição-geral)  
2. [Vantagens e Funcionalidades](#vantagens-e-funcionalidades)  
3. [Pré-Requisitos](#pré-requisitos)  
4. [Estrutura do Repositório](#estrutura-do-repositório)  
5. [Como Utilizar o Parent POM](#como-utilizar-o-parent-pom)  
6. [Como Utilizar o BOM (Bill of Materials)](#como-utilizar-o-bom-bill-of-materials)  
7. [Exemplo de Projeto Filho](#exemplo-de-projeto-filho)  
8. [Boas Práticas e Versionamento](#boas-práticas-e-versionamento)  
9. [Contato](#contato)  
10. [Referências Oficiais](#referências-oficiais)

---

## 📄 Descrição Geral
O objetivo deste repositório é **padronizar** e **simplificar** o desenvolvimento de aplicações Mule. Ao consolidar as configurações mais utilizadas em um **Parent POM**, evitamos a duplicação de configurações em cada projeto. Já o **BOM** gerencia versões de dependências (conectores, libs MUnit etc.) em um único local, garantindo consistência em todo o ecossistema.

---

## ✅ Vantagens e Funcionalidades
- **Plug and Play**: Basta apontar o `parent-pom.xml` e/ou o `bom.xml` no seu projeto Mule, sem precisar copiar configurações de plugin e repositório toda hora.  
- **Menos Duplicação**: Atualiza versões de dependências (ex.: HTTP Connector, Sockets, MUnit) em um lugar só – todos os projetos ficam alinhados.  
- **Governança**: Fácil controle de versões aprovadas e plugins autorizados pela organização.  
- **Facilidade de Deploy**: O `parent-pom.xml` já pode conter configurações de deploy no CloudHub, repositórios privados, etc.  

---

## 🖥️ Pré-Requisitos
- **Maven 3.x** ou superior  
- **Java 8** (Zulu/OpenJDK de preferência)  
- **Conta no Anypoint Platform** (caso deseje publicar ou consumir do Exchange)  
- **Git** para clonar/baixar este repositório (ou acesso direto via Exchange, se publicado lá)

---

## 📂 Estrutura do Repositório

```
mule-parent-bom/
├── parent-pom.xml   (POM Pai para configurações de plugins e build)
├── bom.xml          (Bill of Materials para gerenciar versões de dependências)
└── README.md        (Este guia de uso)
```

### parent-pom.xml
- Define **Plugin Management** para Mule Maven Plugin, MUnit, etc.  
- Configura repositórios Maven (Exchange, MuleSoft releases, repositório privado).  
- Agrupa propriedades globais (por exemplo, `java.version`, `project.build.sourceEncoding`).

### bom.xml
- Centraliza as **versões** das dependências Mule.  
- Usa `<dependencyManagement>` para que projetos filhos possam **importar** essas versões, sem repetir `<version>` no `pom.xml`.

---

## 🔌 Como Utilizar o Parent POM

1. **Incluir o Parent** no `pom.xml` do seu projeto Mule:
   ```xml
   <parent>
       <groupId>com.exemplo</groupId>
       <artifactId>mule-parent</artifactId>
       <version>1.0.0</version>
   </parent>
   ```

2. **Remover configurações duplicadas** que já estão no `parent-pom.xml`, como:
   - `<pluginRepositories>`  
   - `<repositories>`  
   - Versões de plugins Mule, MUnit, etc.  

3. **Personalizar** se necessário:
   - Se você tem propriedades **muito específicas** do projeto (ex.: `<app.runtime>4.6.14</app.runtime>`), deixe-as no `pom.xml` filho.  
   - Se for algo “global” a todos os projetos, coloque no `parent-pom.xml`.  

---

## 📦 Como Utilizar o BOM (Bill of Materials)

1. **Importar o BOM** no `dependencyManagement` do seu projeto:
   ```xml
   <dependencyManagement>
       <dependencies>
           <dependency>
               <groupId>com.exemplo</groupId>
               <artifactId>mule-bom</artifactId>
               <version>1.0.0</version>
               <type>pom</type>
               <scope>import</scope>
           </dependency>
       </dependencies>
   </dependencyManagement>
   ```
2. **Adicionar Dependências Sem Versão**:
   ```xml
   <dependencies>
       <dependency>
           <groupId>org.mule.connectors</groupId>
           <artifactId>mule-http-connector</artifactId>
           <classifier>mule-plugin</classifier>
       </dependency>
       
       <!-- MUnit -->
       <dependency>
           <groupId>com.mulesoft.munit</groupId>
           <artifactId>munit-tools</artifactId>
           <classifier>mule-plugin</classifier>
           <scope>test</scope>
       </dependency>
       ...
   </dependencies>
   ```
   O Maven buscará as versões **definidas** no `bom.xml`.

---

## 🏗️ Exemplo de Projeto Filho
```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         ...
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
    <modelVersion>4.0.0</modelVersion>

    <!-- 1) Referencia o Parent POM -->
    <parent>
        <groupId>com.exemplo</groupId>
        <artifactId>mule-parent</artifactId>
        <version>1.0.0</version>
    </parent>

    <groupId>com.exemplo</groupId>
    <artifactId>meu-projeto-mule</artifactId>
    <version>1.0.0</version>
    <packaging>mule-application</packaging>

    <!-- 2) Importa o BOM para gerenciar versões de dependência -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.exemplo</groupId>
                <artifactId>mule-bom</artifactId>
                <version>1.0.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <!-- 3) Declara somente groupId e artifactId (sem version) -->
    <dependencies>
        <dependency>
            <groupId>org.mule.connectors</groupId>
            <artifactId>mule-http-connector</artifactId>
            <classifier>mule-plugin</classifier>
        </dependency>

        <dependency>
            <groupId>com.mulesoft.munit</groupId>
            <artifactId>munit-tools</artifactId>
            <classifier>mule-plugin</classifier>
            <scope>test</scope>
        </dependency>
        ...
    </dependencies>

    <!-- 4) Demais configurações específicas do projeto -->
    <!-- ... -->

</project>
```

---

## 🔒 Boas Práticas e Versionamento
- **Versionamento Semântico (SemVer)**:  
  - `1.0.0` para a release inicial estável.  
  - `1.1.0` quando adicionar conectores ou plugins novos sem quebrar compatibilidade.  
  - `2.0.0` se houver alterações que quebrem compatibilidade nos projetos filhos.  

- **Revisão de Pull Requests**:  
  - Alterar o BOM pode impactar vários projetos, então sempre valide com o time antes de subir para produção.

- **Publicar no Exchange**:  
  - Considere subir o `parent-pom.xml` e `bom.xml` no Anypoint Exchange.  
  - Assim, desenvolvedores apenas adicionam a dependência do **Exchange** sem precisar baixar do Git diretamente.

---

## 💬 Contato
Para dúvidas ou contribuições, entre em contato com:
- **Leonel Dorneles Porto**  
  [leoneldornelesporto@outlook.com.br](mailto:leoneldornelesporto@outlook.com.br)  
  **+55 53 99180-4869**

---

## 📚 Referências Oficiais
- [Documentação Mule Runtime 4.4](https://docs.mulesoft.com/mule-runtime/4.4/)  
- [Bill of Materials (Maven)](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#bill-of-materials)  
- [Anypoint Exchange](https://docs.mulesoft.com/exchange/)  
- [Mule Maven Plugin](https://docs.mulesoft.com/mule-runtime/4.4/mule-maven-plugin)  
- [MUnit (Testes Automatizados)](https://docs.mulesoft.com/munit/)  

---
