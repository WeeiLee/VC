Ejercicios de Práctica 1

Autores: 
Wei Li 
Anthony Diego Avila Arias 

TAREA 1:

Se crea una matriz de dimensión 800x800 de valor iniciales 0 con un único plano. Se recorre las filas y columnas de un tablero de 8x8 casillas. Cuando se determina la suma de fila y columna en par, se colorea en blanco desde este pixel hasta su siguiente tanto fila como columna multiplicando por 100 (porque la tabla es de 800pixeles).

TAREA 2: 

Primero se crea una imagen en blanco con tres canales. Después se define una lista de colores que servirán para rellenar las distintas zonas. A continuación, se decide aleatoriamente cuántas líneas verticales y horizontales habrá, y también se eligen sus posiciones dentro de la imagen, asegurando que no estén demasiado cerca de los bordes. A esas posiciones se les añaden los límites de la imagen y se ordenan para que formen una cuadrícula bien definida.
Con esas líneas, se generan rectángulos a partir de la intersección de cada par de líneas horizontales y verticales. Cada rectángulo se rellena con un color escogido aleatoriamente de la lista definida al inicio. Finalmente, se dibujan las líneas divisorias en color negro en la imagen.

TAREA 3:
Primero se leen los frames de la cámara y se separan en 3 matrices, una para cada color primario, luego para cada matriz se calcula el cuadrado central de tamaño 1/4 respecto al tamaño total, en esta área los valores menores a 127 se igualan a 0 y los mayores a este se igualan a 255. Finalmente se crea un collage con estas 3 matrices y se muestran en el programa.

TAREA 4:
Se define una función, que gracias a numpy, puede calcular la zona 8x8 más clara y obscura. Dado el frame que se le pasa por parámetro los divide en zonas 8x8 usando 'reshape', luego para cada bloque calcula su promedio usando 'mean', finalmente con 'unravel_index' obtiene la posición de la zona 8x8 más clara y obscura, con esos valores se calcula la posición del pixel central y se devuelve la tupla (x,y).

El resto del código se encarga de leer los frames de la cámara y mostrar el color del pixel que indica el cursor, después de eso se llama a la función que se declaró para calcular la posición de los píxeles de las zonas 8x8, con esos valores se dibujan dos círculos para mostrar en el programa sus posiciones.

TAREA 5:
Se define una función que devuelve el color de un pixel dada su posición en pantalla. Se divide en 4 zonas, y en cada una se calcula el valor opuesto de uno de los colores RGB. 

Luego, en el resto del código, se leen los frames de la cámara y se hace un resize a un tamaño inferior, para poder perder detalle y poder agregar un efecto. Se dibuja una nueva imagen del tamaño original, pero usando los valores de la imagen reducida, se dibujan líneas diagonales con esos valores y se consiguen sus colores usando la función definida anteriormente, de esta forma se crea un Pop Art muy curioso.
