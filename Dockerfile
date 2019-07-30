FROM python:3.5-slim
ENV PYTHONUNBUFFERED 1
ARG PROJECT_SETTINGS

# Fix for "Some index files failed to download", as Jessie's repos have moved to the devian archive.
# https://superuser.com/questions/1423486/issue-with-fetching-http-deb-debian-org-debian-dists-jessie-updates-inrelease
# https://superuser.com/questions/1417617/apt-get-update-is-failing-in-debian/1417656#1417656

RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list

# If dev env install additional packages
RUN  if [ "`echo $PROJECT_SETTINGS | rev | cut -c -3 | rev`" = "dev" ]; then \
       apt-get update; \
       apt-get install -y build-essential graphviz vim tree git tig; \
     fi

RUN apt-get update && \
        apt-get install -y \
                netcat \
        && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /source/
WORKDIR /source
RUN pip install -r requirements.txt
ADD . /source/

RUN chmod +x /source/docker-entrypoint.sh
EXPOSE 8000
CMD ["/source/docker-entrypoint.sh"]
