question:
Udało mi się przejść tutorial i uruchomić przykładowy scenariusz lokalnie.

Klient działa poprawnie przy konfiguracji:

from graft_pypi_graftcode_tutorial.energypricecalculator import EnergyPriceCalculator
from graft_pypi_graftcode_tutorial.graft.pypi.graftcode_tutorial.graft_config import GraftConfig

GraftConfig.host = "ws://localhost/ws"

result = EnergyPriceCalculator.get_price()


Dodatkowo utworzyłem projekt, uruchomiłem Gateway z wygenerowanym Project Key i portal potwierdził rejestrację Gateway (Gateway discovered).

image.png

Niestety po zakończeniu konfiguracji widok Gateway w portalu zwraca błąd („Something went wrong”)

image.png

W związku z tym mam kilka pytań odnośnie LOCAL i REMOTE:


Czy oczekiwane rozwiązanie ma wyglądać w stylu port-adapter, gdzie Order Service korzysta z jednego interfejsu, a implementacja jest wybierana konfiguracją:

Opcja A:
LOCAL:
Order Service -> lokalna implementacja Pricing Service (bez Graftcode)

REMOTE:
Order Service -> Graft -> Gateway -> Pricing Service

czy też opcja B:

LOCAL:
Order Service -> Graft -> lokalny Gateway (localhost)

REMOTE:
Order Service -> Graft -> Gateway zarejestrowany w projekcie


Czy portal udostępnia później adres Gateway (analogiczny do ws://localhost/ws), z którego powinien korzystać klient?

image.png
Obecnie, ze względu na błędy widoczne w sekcji Gateway w portalu, nie jestem w stanie sprawdzić, jakie informacje powinny być tam dostępne po poprawnej rejestracji.

W związku z tym chciałbym również upewnić się, czy na potrzeby zadania akceptowalne jest rozwiązanie wykorzystujące Graftcode i wygenerowane Grafty, ale komunikujące się z lokalnie uruchomionym Gateway (zgodnie z tutorialem), czy oczekiwane jest wykorzystanie infrastruktury powiązanej z Project Key i zarejestrowanym Gateway.

Z góry dziękuję za odpowiedź :)

PS.
Wiem, że to Alpha - ale może się przyda na przyszłość takie info: 

Podczas uruchamiania na macOS (Apple Silicon) musiałem użyć obrazu/artefaktów ARM (arm64), a przy instalacji wygenerowanego klienta przez uv konieczne było użycie --index-strategy unsafe-best-match, aby poprawnie rozwiązać zależności


Recruiter answer:
Bardziej opcja:
Local:
Order service -> graft Pricing Service -> PricingService (Na start wyhostowany przez GG) zeby zuploadowac modul I moc zainstalowac grafta
Remote:
Order service - graft Pricing Service -> PricingService(hostowany przez gg)

Nawet przy remote masz hostowanie przez local bo podzial remote I local nie chodzi o adresy tylko o to czy jest to przez websocket/tcp albo w jednym procesie in memory