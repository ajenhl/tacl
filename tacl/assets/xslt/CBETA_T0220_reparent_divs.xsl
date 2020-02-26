<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:cb="http://www.cbeta.org/ns/1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <!-- Move the cb:div[@type='pin'] from T06n0220b to the end of the
       cb:div[@type='hui'] from T05n0220a. -->

  <xsl:template match="tei:TEI[@xml:id='T05n0220a']//cb:div[@type='hui']">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
      <xsl:copy-of select="/tei:teiCorpus/tei:TEI[@xml:id='T06n0220b']//cb:div[@type='pin']" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="tei:TEI[@xml:id='T06n0220b']" />

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
