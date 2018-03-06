from django.db                import models

from Crypto.PublicKey         import RSA

class PrivateKey( models.Model ):
    poll        = models.ForeignKey( 'poll.Poll', verbose_name = 'ankieta' , on_delete=models.CASCADE)
    private_key = models.TextField(  verbose_name = 'klucz prywatny' )

    class Meta:
        verbose_name        = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label           = 'ticket_create'

    def __str__( self ):
        return "Klucz prywatny: " + str( self.poll )

    def sign_ticket( self, ticket ):
        key     = RSA.importKey( self.private_key )
        return key.sign( ticket, 0 )

    def verify_signature( self, ticket, signed_ticket ):
        key     = RSA.importKey( self.private_key )
        return key.verify( ticket, signed_ticket )
