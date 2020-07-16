CREATE TABLE IF NOT EXISTS provincia (
  p_id TINYINT NOT NULL PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL ,
  codigo31662 CHAR(4) NOT NULL);

CREATE TABLE IF NOT EXISTS localidad (
  l_id INT(10)  NOT NULL PRIMARY KEY ,
  provincia_id TINYINT  NOT NULL ,
  nombre VARCHAR(50) NOT NULL ,
  codigopostal SMALLINT(6) NOT NULL ,
  FOREIGN KEY (l_id) REFERENCES provincia(p_id)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION);

CREATE TABLE IF NOT EXISTS comunas_capital (
    c_id TINYINT NOT NULL PRIMARY KEY,
    provincia_id TINYINT  NOT NULL ,
    barrio ARCHAR(50) NOT NULL,
    comuna INT(2) NOT NULL,
    codigopostal SMALLINT(6) NOT NULL,
    FOREIGN KEY (c_id) REFERENCES provincia(p_id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);