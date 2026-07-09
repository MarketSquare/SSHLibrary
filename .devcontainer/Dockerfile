FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash-completion \
        ca-certificates \
        gcc \
        git \
        language-pack-en \
        libffi-dev \
        locales \
        make \
        musl-dev \
        net-tools \
        openssh-client \
        openssh-server \
        python3 \
        python3-pip \
        python3-venv \
        sudo \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN mkdir -p /run/sshd \
    && useradd --create-home --shell /bin/bash test-nopasswd \
    && passwd --delete test-nopasswd \
    && echo "PermitEmptyPasswords yes" >> /etc/ssh/sshd_config \
    && useradd --create-home --shell /bin/bash test \
    && (echo 'test'; echo 'test') | passwd test \
    && adduser test sudo \
    && echo 'test   ALL=(ALL:ALL) PASSWD:ALL' > /etc/sudoers.d/passworded \
    && chmod 0440 /etc/sudoers.d/passworded \
    && useradd --create-home --shell /bin/bash testkey \
    && echo "export PS1='\\u@\\h \\W \\$ '" >> /home/test/.bashrc \
    && echo "export PS1='\\u@\\h \\W \\$ '" >> /home/testkey/.bashrc \
    && sudo -u testkey mkdir -p /home/testkey/.ssh \
    && sudo -u testkey ssh-keygen -f /home/testkey/.ssh/id_rsa -t rsa -N '' \
    && sudo -u testkey cp /home/testkey/.ssh/id_rsa.pub /home/testkey/.ssh/authorized_keys \
    && chmod 700 /home/testkey/.ssh \
    && chmod 600 /home/testkey/.ssh/authorized_keys \
    && chmod 644 /home/testkey/.ssh/id_rsa \
    && echo 'Testing pre-login banner' > /etc/ssh/sshd-banner \
    && echo 'Banner /etc/ssh/sshd-banner' >> /etc/ssh/sshd_config \
    && echo 'Subsystem subsys echo "Subsystem invoked."' >> /etc/ssh/sshd_config \
    && mkdir -p /root/.ssh \
    && printf 'Host test_hostname\n    Hostname localhost\n' >> /root/.ssh/config

CMD ["sleep", "infinity"]
