#include <stdio.h>
#include <stdlib.h>

void normalServer();
void primeServer();
void sumServer();

int main() {
    int choice;

    do {
        printf("\nMenu:\n");
        printf("1. Normal Server\n");
        printf("2. Prime Number Server\n");
        printf("3. Sum Server\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                normalServer();
                break;
            case 2:
                primeServer();
                break;
            case 3:
                sumServer();
                break;
            case 4:
                printf("Exiting the program.\n");
                break;
            default:
                printf("Invalid choice. Please enter a number between 1 and 4.\n");
        }
    } while (choice != 4);

    return 0;
}

void normalServer() {
    #include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h> // Include for the close function

int main() {
    int sockfd, i;
    char buf[100];
    /* We will use this buffer for communication */
    struct sockaddr_in sa, ta;

    int port = 60018; // Hardcoded port number

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd == -1) {
        perror("socket");
        return 1;
    }

    sa.sin_family = AF_INET;
    sa.sin_addr.s_addr = htonl(INADDR_ANY);
    sa.sin_port = htons(port);
    memset(&(sa.sin_zero), '\0', 8);
    i = bind(sockfd, (struct sockaddr *)&sa, sizeof(sa));
    if (i == -1) {
        perror("bind");
        return 1;
    }

    /* We again initialize the buffer, and receive a message from the client. */
    for (i = 0; i < 100; i++) buf[i] = '\0';

    socklen_t ta_len = sizeof(ta);
    ssize_t bytes_received = recvfrom(sockfd, buf, 100, 0, (struct sockaddr *)&ta, &ta_len);
    if (bytes_received == -1) {
        perror("recvfrom");
        return 1;
    }

    printf("Received message from IP: %s and port: %i\n", inet_ntoa(ta.sin_addr), ntohs(ta.sin_port));
    printf("Msg from client: %s\n", buf);

    /* We initialize the buffer, copy the message to it,
    and send the message to the client. */
    for (i = 0; i < 100; i++) buf[i] = '\0';
    strcpy(buf, "Message from server");
    ssize_t bytes_sent = sendto(sockfd, buf, 100, 0, (struct sockaddr *)&ta, ta_len);
    if (bytes_sent == -1) {
        perror("sendto");
        return 1;
    }
    close(sockfd);

    return 0;
}


    printf("Normal Server executed.\n");
}

void primeServer() {
   #include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
int main()
{
    int sockfd, i;
    struct sockaddr_in sa, ta;       // The structure "sockaddr_in" is defined in <netinet/in.h> for the internet family of protocol>    // char buf[100];                   // We will use this buffer for communication.


    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    sa.sin_family = AF_INET;
    sa.sin_addr.s_addr = htonl(INADDR_ANY);            // can be used inet_addr("127.0.0.1")
    sa.sin_port = htons(60018);
    memset(&(sa.sin_zero), '\0', 8);


    i = bind(sockfd, (struct sockaddr *)&sa, sizeof(sa));
    printf("test %d %d\n", sockfd, i);


    /* We again initialize the buffer, and receive a  message from the client. */
    // for (i = 0; i < 100; i++)
    //     buf[i] = '\0';
        int x = sizeof(sa);

    int n;
    // recvfrom(sockfd, buf, 100, 0, (struct sockaddr *)&ta, &x);
    recvfrom(sockfd, &n, sizeof n, 0, (struct sockaddr *)&ta, &x);

    for(int x = n + 1; 1; x++) {
        int flag = 0;
        for(int i = 2; i*i <= x; i++) {
            if(x % i == 0) {
                flag = 1;
                break;
            }
        }
        if(!flag) {
            sendto(sockfd, &x, sizeof x, 0, (struct sockaddr *)&ta, sizeof(ta));
            close(sockfd);
            return 0;
        }
    }
}

    printf("Prime Number Server executed.\n");
}

void sumServer() {
    #include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
int main()
{
    int sockfd, i;
    struct sockaddr_in sa, ta;       // The structure "sockaddr_in" is defined in <netinet/in.h> for the internet family of protocol>    // char buf[100];                   // We will use this buffer for communication.


    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    sa.sin_family = AF_INET;
    sa.sin_addr.s_addr = htonl(INADDR_ANY);            // can be used inet_addr("127.0.0.1")
    sa.sin_port = htons(60018);
    memset(&(sa.sin_zero), '\0', 8);


    i = bind(sockfd, (struct sockaddr *)&sa, sizeof(sa));
    printf("test %d %d\n", sockfd, i);


    /* We again initialize the buffer, and receive a  message from the client. */
    // for (i = 0; i < 100; i++)
    //     buf[i] = '\0';
    int x = sizeof(sa);

    int a, b;
    // recvfrom(sockfd, buf, 100, 0, (struct sockaddr *)&ta, &x);
    recvfrom(sockfd, &a, sizeof a, 0, (struct sockaddr *)&ta, &x);
    recvfrom(sockfd, &b, sizeof b, 0, (struct sockaddr *)&ta, &x);

    a += b;


    // printf("Received message from IP: %s and port: %i\n", inet_ntoa(ta.sin_addr), ntohs(ta.sin_port));
    // printf("Msg from client: %s\n", buf);


    /* We initialize the buffer, copy the message to it,
    and send the message to the client. */
    // for (i = 0; i < 100; i++)
    //     buf[i] = '\0';
    // strcpy(buf, "Message from server");
    sendto(sockfd, &a, sizeof a, 0, (struct sockaddr *)&ta, sizeof(ta));


    close(sockfd);
    return 0;
}

    printf("Sum Server executed.\n");
}
