from sqlmodel import Relationship
from src.models.client import Client
from src.models.object import Object
from src.models.verb import Verb
from src.models.faq import Faq
from src.models.domain import Domain
from src.models.contact import Contact
from src.models.log import Log
from src.models.log_faq import LogFaq
from src.models.log_reset_password import LogResetPassword

print("--- Loading model relationships ---")
# Load client relationships
Client.contacts = Relationship(
    back_populates="client", sa_relationship_kwargs={"lazy": "selectin"})
Contact.client = Relationship(
    back_populates="contacts", sa_relationship_kwargs={"lazy": "selectin"})
Client.domains = Relationship(
    back_populates="client", sa_relationship_kwargs={"lazy": "selectin"})
Domain.client = Relationship(
    back_populates="domains", sa_relationship_kwargs={"lazy": "selectin"})
Client.objects = Relationship(
    back_populates="client", sa_relationship_kwargs={"lazy": "selectin"})
Object.client = Relationship(
    back_populates="objects", sa_relationship_kwargs={"lazy": "selectin"})
Client.faqs = Relationship(back_populates="client",
                           sa_relationship_kwargs={"lazy": "selectin"})
Faq.client = Relationship(back_populates="faqs",
                          sa_relationship_kwargs={"lazy": "selectin"})
Client.logs = Relationship(back_populates="client",
                           sa_relationship_kwargs={"lazy": "selectin"})
Log.client = Relationship(back_populates="logs",
                          sa_relationship_kwargs={"lazy": "selectin"})
Client.log_faqs = Relationship(
    back_populates="client", sa_relationship_kwargs={"lazy": "selectin"})
LogFaq.client = Relationship(
    back_populates="log_faqs", sa_relationship_kwargs={"lazy": "selectin"})
Client.log_reset_passwords = Relationship(
    back_populates="client", sa_relationship_kwargs={"lazy": "selectin"})
LogResetPassword.client = Relationship(
    back_populates="log_reset_passwords", sa_relationship_kwargs={"lazy": "selectin"})

# print("--- Load Faq relationships ---")
Faq.object = Relationship(back_populates="faqs",
                          sa_relationship_kwargs={"lazy": "selectin"})
Object.faqs = Relationship(back_populates="object",
                           sa_relationship_kwargs={"lazy": "selectin"})
Faq.verb = Relationship(back_populates="faqs",
                        sa_relationship_kwargs={"lazy": "selectin"})
Verb.faqs = Relationship(back_populates="verb",
                         sa_relationship_kwargs={"lazy": "selectin"})
Faq.log_faqs = Relationship(
    back_populates="faq", sa_relationship_kwargs={"lazy": "selectin"})
LogFaq.faq = Relationship(back_populates="log_faqs",
                          sa_relationship_kwargs={"lazy": "selectin"})

# print("--- Load Verb relationships ---")
Verb.log_faqs = Relationship(
    back_populates="verb", sa_relationship_kwargs={"lazy": "selectin"})
LogFaq.verb = Relationship(back_populates="log_faqs",
                           sa_relationship_kwargs={"lazy": "selectin"})

# print("--- Load Object relationships ---")
Object.log_faqs = Relationship(
    back_populates="object", sa_relationship_kwargs={"lazy": "selectin"})
LogFaq.object = Relationship(
    back_populates="log_faqs", sa_relationship_kwargs={"lazy": "selectin"})

# print("--- Load Object relationships ---")
Object.log_faqs = Relationship(
    back_populates="object", sa_relationship_kwargs={"lazy": "selectin"})
LogFaq.object = Relationship(
    back_populates="log_faqs", sa_relationship_kwargs={"lazy": "selectin"})
print("--- Model relationships loaded ---")
