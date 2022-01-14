FROM ubuntu:16.04
RUN apt-get update -y
RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update
RUN apt-get install -y python3.7 python3-pip gcc make musl-dev libffi-dev net-tools language-pack-en locales
RUN python3.7 -m pip install --upgrade pip
RUN python3.7 -m pip install --upgrade robotframework-sshlibrary robotbackgroundlogger robotstatuschecker
ARG repository
RUN apt-get install -y openssh-server sudo git
RUN useradd --create-home --shell /bin/bash test-nopasswd
RUN passwd --delete test-nopasswd
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN systemctl restart sshd
RUN useradd test --create-home --shell /bin/bash test
RUN (echo 'test'; echo 'test') | passwd test
RUN echo -e "test\n test" | adduser test sudo
RUN sh -c "echo 'test   ALL=(ALL:ALL) PASSWD:ALL' > /etc/sudoers.d/passworded"
RUN useradd -m testkey -s /bin/bash
RUN sudo -E su test -c echo "$'export PS1='\u@\h \W \$ '' >> /home/test/.bashrc"
RUN sudo -E su testkey -c echo "$'export PS1='\u@\h \W \$ '' >> /home/testkey/.bashrc"
RUN sudo -E su testkey -c "mkdir -p /home/testkey/.ssh"
RUN sudo -E su testkey -c "ssh-keygen -f /home/testkey/.ssh/id_rsa -t rsa -N ''"
RUN sudo -E su testkey -c "cp /home/testkey/.ssh/id_rsa.pub /home/testkey/.ssh/authorized_keys"
RUN sudo -E su testkey -c "chmod 644 /home/testkey/.ssh/id_rsa"
RUN git clone $repository
RUN cp /home/testkey/.ssh/id_rsa /SSHLibrary/atest/testdata/keyfiles/
RUN echo 'Testing pre-login banner' >> /etc/ssh/sshd-banner
RUN echo 'Banner /etc/ssh/sshd-banner' >> /etc/ssh/sshd_config
RUN echo 'Subsystem subsys echo "Subsystem invoked."' >> /etc/ssh/sshd_config
RUN sudo mkdir -p ~/.ssh
RUN echo 'Host test_hostname\n    Hostname localhost\n' >> ~/.ssh/config
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
