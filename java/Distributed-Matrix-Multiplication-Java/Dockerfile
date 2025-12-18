FROM maven:3.9-eclipse-temurin-11 AS build

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src

RUN mvn clean package -DskipTests

FROM eclipse-temurin:11-jre-focal

WORKDIR /app

COPY --from=build /app/target/distributed-matrix-multiplication-1.0-SNAPSHOT.jar app.jar

RUN mkdir -p results

CMD ["java", "-Xmx4g", "-jar", "app.jar"]
