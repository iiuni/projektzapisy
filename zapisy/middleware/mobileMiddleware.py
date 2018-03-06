from django.http import HttpResponseRedirect

class SubdomainMiddleware:
    """
        Klasa odpowiedzialna za przekierowania do i z subdomeny mobilnej m.
    """
    def process_request(self, request):
        domain = request.META.get('HTTP_HOST', '')
        parts = domain.replace('www.', '').split('.')
        #jeśli użytkownik zdecydował, że nie chce wersji mobilnej
        if 'no_mobile' in request.session and request.session['no_mobile'] == True:
            #adres mobilny wybrany bezpośrednio
            if parts[0] == 'm':
                request.META['HTTP_HOST'] = domain
                request.mobile = True
                request.urlconf = 'zapisy.mobile_urls'#'mobile.urls'
            else:
                request.mobile = False

        elif parts[0] == 'm':
            request.mobile = True
            request.urlconf = 'zapisy.mobile_urls'

        #wiadomość przekazana z mobileDetection - wykryto urządzenie mobilne
        elif request.is_mobile:
            request.META['HTTP_HOST'] = 'm.' + domain.replace('www.', '')
            request.mobile = True
            request.urlconf = 'zapisy.mobile_urls'
            return HttpResponseRedirect(request.path)

        else:
            request.mobile = False
