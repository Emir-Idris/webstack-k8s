FROM alpine:3.19

RUN apk add --no-cache lighttpd
RUN mkdir -p /run/lighttpd

COPY index.html /var/www/localhost/htdocs/index.html
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

EXPOSE 80
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
