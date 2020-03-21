FROM python:3.7.6

LABEL maintainer="aditya.garg@columbia.edu"

ADD requirements.txt /tmp/requirements.txt

# install all python dependencies
RUN pip install -r /tmp/requirements.txt 

ADD ./fact_check_me /fact_check_me

EXPOSE 8050

CMD ["gunicorn", "-w 4", "-k gevent", "-b 0.0.0.0:8050", "fact_check_me.app:APP", "--timeout 120", "--graceful-timeout 120"]
