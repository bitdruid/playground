FROM python:3.11-slim AS whois
RUN apt -qq update && apt -qq install -y whois

FROM python:3.11-slim AS requirements
WORKDIR /app
COPY requirements-bot.txt /app
RUN pip3 install --upgrade pip && pip3 install -r requirements-bot.txt
COPY osintkit/ /app/osintkit/
COPY setup.py /app
COPY requirements-kit.txt /app
RUN pip install .

FROM python:3.11-slim
WORKDIR /app
COPY --from=whois /usr/bin/whois /usr/bin/whois
COPY --from=requirements /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=requirements /usr/local/bin /usr/local/bin
RUN pip install playwright
RUN playwright install --with-deps firefox
COPY osintbot/* /app/osintbot/

EXPOSE 5001
EXPOSE 5002
COPY weblog.py /app
COPY start.py /app
CMD ["python3", "start.py"]