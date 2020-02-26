<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <!-- Output the document with its contents only up to (but not
       including) tei:lb[@n='0861a08']. -->

  <xsl:template match="*">
    <xsl:if test=".//tei:lb[@n='0861a08'] or following::tei:lb[@n='0861a08']">
      <xsl:copy>
        <xsl:apply-templates select="@*|node()" />
      </xsl:copy>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@*">
    <xsl:copy-of select="." />
  </xsl:template>

  <xsl:template match="text()">
    <xsl:if test="following::tei:lb[@n='0861a08']">
      <xsl:copy />
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
