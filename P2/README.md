Ejercicios de Práctica 2
Autores: Wei Li, Anthony Diego Avila Arias 

Tarea 1:  Realiza la cuenta de píxeles blancos por filas (en lugar de por columnas). Determina el valor máximo de píxeles blancos para filas, maxfil, mostrando el número de filas y sus respectivas posiciones, con un número de píxeles blancos mayor o igual que 0.90*maxfil.

Se utiliza la función "reduce" sobre la imagen obtenida con Canny, especificando la dimensión 1 para sumar los píxeles blancos a lo largo de cada fila. Luego se aplica "transpose" para convertir el resultado en un array con la suma de cada fila. A continuación, se identifica la fila que contiene el máximo número de píxeles blancos.

Después, se itera sobre todas las filas para encontrar aquellas que alcanzan al menos el 90% de ese máximo, registrando sus posiciones. Finalmente, se muestran la imagen de Canny y un histograma normalizado que representa la intensidad de píxeles blancos por fila.




Tarea 2: Aplica umbralizado a la imagen resultante de Sobel (convertida a 8 bits), y posteriormente realiza el conteo por filas y columnas similar al realizado en el ejemplo con la salida de Canny de píxeles no nulos. Calcula el valor máximo de la cuenta por filas y columnas, y determina las filas y columnas por encima del 0.90*máximo. Remarca con alguna primitiva gráfica dichas filas y columnas sobre la imagen del mandril. ¿Cómo se comparan los resultados obtenidos a partir de Sobel y Canny?

Primero, la imagen en escala de grises se suaviza usando un filtro gaussiano. Luego se aplican los operadores Sobel en dirección horizontal y vertical, y se combinan ambos resultados para obtener los bordes de la imagen.

A continuación, se convierte la imagen Sobel a valores absolutos de 8 bits y se aplica un umbral fijo, generando una versión binarizada donde los píxeles con intensidad por encima del umbral se consideran bordes.

Se calcula la suma de píxeles blancos por fila y columna, identificando aquellas filas y columnas que contienen al menos el 90% del valor máximo detectado. Estas posiciones se usan para trazar líneas sobre la imagen Sobel, destacando las zonas con mayor densidad de bordes.

Además, se generan versiones comparativas:

1.Comparación entre Canny y Sobel filtrado con inRange, mostrando la diferencia absoluta entre ambos métodos.
2.Comparación entre Canny y la Sobel umbralizada, visualizando qué bordes coinciden y cuáles son exclusivos de cada método.





Tarea3: Proponer un demostrador que capture las imágenes de la cámara, y les permita exhibir lo aprendido en estas dos prácticas ante quienes no cursen la asignatura :). Es por ello que además de poder mostrar la imagen original de la webcam, permita cambiar de modo, incluyendo al menos dos procesamientos diferentes como resultado de aplicar las funciones de OpenCV trabajadas hasta ahora.

El código captura video en tiempo real y permite cambiar entre modo diferencia y modo Canny:

Modo Diferencia:
Se calcula la diferencia absoluta entre el fotograma actual y uno anterior, permitiendo resaltar cambios en la escena. Se guarda un historial limitado de los últimos 20 fotogramas para el cálculo del modo diferencia, evitando que la comparación use fotogramas muy antiguos. El parámetro "wait_value" define cuántos fotogramas atrás se compara y puede ajustarse con el teclado.

Modo Canny:
Se aplican los operadores de Canny para detectar bordes del fotograma actual. Se pueden ajustar dos umbrales "first_treshold" y "second_treshold" con el teclado, y alternar cuál de los dos se está modificando.

Análisis de intensidad de bordes:
Se calcula la suma de píxeles de borde por fila y columna.
Se dibujan líneas rojas y azules sobre las filas y columnas que contienen al menos el 90% de píxeles de borde más intensos, resaltando las zonas con mayor densidad de contornos. Y se genera un histograma de los bordes en la imagen como líneas amarillas sobre el fotograma.

Selección:
Teclas A/D → Cambiar entre los modos Diferencia y Canny.
Teclas W/S → Ajustar valores de espera o umbrales según el modo.
Tecla Q → Alternar cuál umbral se está modificando en Canny.
Tecla ESC → Salir del programa.



Tarea 4: Tras ver los vídeos [My little piece of privacy](https://www.niklasroy.com/project/88/my-little-piece-of-privacy), [Messa di voce](https://youtu.be/GfoqiyB1ndE?feature=shared) y [Virtual air guitar](https://youtu.be/FIAmyoEpV5c?feature=shared) proponer un demostrador reinterpretando la parte de procesamiento de la imagen, tomando como punto de partida alguna de dichas instalaciones.

Respuesta 1:

El código muestra inicialmente una pantalla negra. Cuando se coloca un objeto azul delante de la cámara, la zona correspondiente se pinta de blanco en la pantalla. Cuando se muestra un objeto rojo, la marca blanca se borra y la zona se vuelve negra.

Detección de color:
Se definen rangos de intensidad para los canales Rojo, Verde y Azul mediante un umbral "treshold" y un valor de compensación "substract".
Para el color rojo, se seleccionan píxeles donde el canal rojo es bajo, el canal azul es alto y el canal verde es bajo.
Para el color azul, se seleccionan píxeles donde el canal azul es bajo, el canal rojo es alto y el canal verde es bajo.

Cuando los píxeles cumplen las condiciones correspondientes, se considera que se ha detectado ese color en la imagen. Dependiendo de si el color detectado es rojo o azul, se pinta la zona en negro o blanco, respectivamente.



Respuesta 2(alternativa): 

El código captura vídeo y realiza detección de movimiento para delimitar un rectángulo alrededor del objeto en movimiento.
Se obtiene la máscara de los objetos en movimiento comparando el fotograma actual con el fondo.
A partir de la máscara se calculan los dos puntos de las esquinas (superior izquierda e inferior derecha) que encierran el objeto detectado, y se dibuja un rectángulo rojo sólido sobre la imagen original para marcar la zona de movimiento.
Si no hay suficiente movimiento, el rectángulo mantiene su posición anterior, evitando que desaparezca abruptamente.