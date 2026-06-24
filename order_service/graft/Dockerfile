FROM python:3.13-bookworm

WORKDIR /usr/app

COPY . /usr/app

RUN apt-get update \
 && apt-get install -y wget \
 && wget -O /usr/app/gg.deb https://github.com/grft-dev/graftcode-gateway/releases/latest/download/gg_linux_arm64.deb \
 && dpkg -i /usr/app/gg.deb \
 && rm /usr/app/gg.deb \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 # NOTE: The GUID in this URL is tied to the running gg instance and changes on every restart.
 # After restarting pricing-graft, update this URL from `make setup` output before rebuilding with --no-cache.
 && pip install --no-cache-dir \
      --extra-index-url https://grft.dev/simple/f812a82c-cdeb-4928-bf7e-c9e6e222e5c2__free \
      graft-pypi-pricing-service-graft==0.1.0

EXPOSE 80
EXPOSE 81

CMD ["gg", "--modules", "./order_service/graft/"]

#
