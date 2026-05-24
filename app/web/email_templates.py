"""Textos prontos para e-mails de contato do site."""


LIST_PET_SUBJECT = "Quero colocar um pet para adoção"

LIST_PET_BODY = """Olá! Gostaria de divulgar um pet para adoção no site.

Preencha as informações abaixo (pode editar este e-mail antes de enviar):

SOBRE O PET
• Nome do pet:
• Espécie (gato ou cão):
• Raça:
• Idade (anos):
• Temperamento (dócil, tímido, brincalhão...):
• Descrição (histórico, saúde, convivência com crianças/outros pets):
• Vacinado: (sim/não)
• Castrado: (sim/não)
• Foto: (anexe imagens a este e-mail)

SEUS DADOS (responsável pelo pet)
• Seu nome:
• Telefone/WhatsApp:
• Cidade/bairro:

Aguardo retorno. Obrigado(a)!"""


def adopt_pet_subject(pet_name: str) -> str:
    return f"Interesse em adotar {pet_name}"


def adopt_pet_body(pet_name: str, pet_type: str, profile_url: str) -> str:
    return f"""Olá! Tenho interesse em adotar o {pet_type} {pet_name}.

Vi o perfil em: {profile_url}

Preencha seus dados abaixo:

• Nome completo:
• Telefone/WhatsApp:
• Cidade/bairro:
• Moradia (casa/apartamento, tem quintal?):
• Experiência com pets:
• Outros pets ou crianças em casa:

Aguardo contato. Obrigado(a)!"""
